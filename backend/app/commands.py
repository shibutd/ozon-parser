import sys
import json
from collections import Counter

import click
from flask import Blueprint
from sqlalchemy.sql import expression
from sqlalchemy_utils.types.ltree import LQUERY

from app import db
from app.parser import Parser
from app.models import Category, Item, Price


cmd_bp = Blueprint('cmd', __name__)


BASE_URL = 'https://ozon.ru'


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance, True


def create_prices(prices_list, item):
    for price_dict in prices_list:
        price_dict.update({'item_id': item.id})
    db.session.bulk_insert_mappings(Price, prices_list)


def create_items(items_list, counter, category):
    for item_dict in items_list:
        item, created = get_or_create(
            db.session,
            Item,
            name=item_dict['name'],
            url=item_dict['externalUrl'],
            category=category
        )
        counter['items'] += 1
        if created:
            counter['items_created'] += 1

        if 'prices' in item_dict:
            db.session.flush()
            create_prices(item_dict['prices'], item)


def create_categories(categories_list, counter, parent=None):
    for category_dict in categories_list:
        category, created = get_or_create(
            db.session,
            Category,
            name=category_dict['name'],
            url=category_dict['url'],
            parent=parent
        )
        counter['categories'] += 1
        if created:
            counter['categories_created'] += 1

        if 'children' in category_dict:
            create_categories(
                category_dict['children'],
                counter=counter,
                parent=category
            )

        if 'items' in category_dict:
            create_items(
                category_dict['items'],
                counter=counter,
                category=category
            )


@cmd_bp.cli.command()
@click.argument('path')
def import_data(path):
    """Import data from .json file."""
    try:
        with open(path, 'r') as jsonfile:
            loaded_json = json.load(jsonfile)

    except FileNotFoundError:
        print('File not found: {}'.format(path), file=sys.stdout)
        sys.exit()

    print('Importing data...', file=sys.stdout)

    c = Counter()

    try:
        create_categories(loaded_json, counter=c)
    except Exception as e:
        db.session.rollback()
        print('Error occured while importing data: {}'.format(e),
              file=sys.stdout)
        sys.exit()

    db.session.commit()

    print(
        "Categories processed={0} (created={1})".format(
            c["categories"], c["categories_created"]),
        file=sys.stdout
    )
    print(
        "Items processed={0} (created={1})".format(
            c["items"], c["items_created"]),
        file=sys.stdout
    )


def get_and_create_parent_categories(parser):
    categories = parser.get_parent_categories(BASE_URL)
    categories = categories[0][BASE_URL]

    db.session.bulk_save_objects(
        [
            Category(
                name=category['name'],
                url=category['url'],
            )
            for category in categories
        ]
    )
    db.session.commit()


def create_subcategories(subcategories, parent_category):
    subcategories_objs = []
    children = []
    for subcategory in subcategories:
        try:
            subcategory_obj = Category(
                name=subcategory['name'],
                url=subcategory['url'],
                parent=parent_category
            )
        except AttributeError:
            continue

        subcategories_objs.append(subcategory_obj)

        sections = subcategory.get('sections')
        if sections:
            children.append((sections, subcategory_obj))

    db.session.bulk_save_objects(subcategories_objs)
    for child in children:
        subcategories, parent_category = child[0], child[1]
        create_subcategories(subcategories, parent_category)


def get_and_create_subcategories(parser):
    # Get parent categories
    parent_categories = Category.query.filter(
        db.func.nlevel(Category.path) == 1).all()

    def get_url(url):
        return '{0}{1}'.format(BASE_URL, url)

    urls = [get_url(parent_category.url)
            for parent_category in parent_categories]

    subcategories = parser.get_subcategories(urls)

    with open('subcategories.json', 'w', encoding='utf-8') as f:
        json.dump(subcategories, f, indent=2, ensure_ascii=False)

    merged_subcategories = {}
    for subcategory in subcategories:
        merged_subcategories.update(subcategory)

    for parent_category, url in zip(parent_categories, urls):
        children = merged_subcategories[url]
        create_subcategories(children, parent_category)
        db.session.commit()


def get_and_create_items(parser):
    i = 1
    # get leaves categories
    parent_categories = Category.query.filter(
        db.func.nlevel(Category.path) == 1).all()

    for parent_category in parent_categories:
        query = '%s.*{2}' % (parent_category.slug)
        lquery = expression.cast(query, LQUERY)

        leaf_categories = Category.query.filter(
            Category.path.lquery(lquery)).all()

        for leaf_category in leaf_categories:
            for items in parser.get_items(leaf_category.url):

                # SAVE TO .JSON FILE
                with open('sample_{}.json'.format(i), 'w',
                          encoding='utf-8') as f:
                    json.dump(items, f, indent=2, ensure_ascii=False)

                    print(
                        f'{len(items)} items saved to sample_{i}.json',
                        file=sys.stdout
                    )
                    i += 1

                    # SAVE ITEMS TO DB
                #     items_objs = []
                #     prices = []
                #     for item in items:
                #         item_obj = Item(
                #             name=item['name'],
                #             url=item['external_url'],
                #             image_url=item['image_url'],
                #             category=leaf_category
                #         )
                #         items_objs.append(item_obj)
                #         # SAVE PRICE TO DB
                #         prices.append(
                #             {
                #                 'value': item['price'],
                #                 'item_id': item_obj.id
                #             }
                #         )
                #     db.session.bulk_save_objects(items_objs)
                #     db.session.flush()

                # db.session.bulk_insert_mappings(Price, prices)
                # db.session.commit()


@cmd_bp.cli.command()
@click.option('-p', '--parse',
              help='Categories, subcategories or items',
              required=True)
def launch_parser(parse):
    """Parse data from 'ozon.ru' and save to db or .json file."""
    if not isinstance(parse, str) or \
            parse.lower() not in ['categories', 'subcategories', 'items']:
        print('Invalid --parse type. Should be "categories", "subcategories" or "items"',
              file=sys.stdout)
        sys.exit()

    parser_functions = {
        'categories': get_and_create_parent_categories,
        'subcategories': get_and_create_subcategories,
        'items': get_and_create_items
    }

    function = parser_functions[parse]
    parser = Parser()
    try:
        function(parser)
    except Exception as e:
        db.session.rollback()
        print('Error occured while adding data: {}'.format(e),
              file=sys.stdout)
        sys.exit()

    print('Successfully parsed data and added to db', file=sys.stdout)
