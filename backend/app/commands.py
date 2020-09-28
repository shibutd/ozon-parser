import sys
import json
from collections import Counter
import click
from flask import Blueprint
from app import db
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
            external_id=item_dict['externalId'],
            category=category,
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
        print('Error occured while importing data: {}'.format(e), file=sys.stdout)
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


@cmd_bp.cli.command()
@click.option('-t', '--type',
              help='Categories, subcategories or items',
              required=True)
def launch_parser(type):
    if type.lower() not in ['categories', 'subcategories', 'items']:
        print('Invalid type. Should be "categories", "subcategories" or "items"',
              file=sys.stdout)
        sys.exit()

    if type == 'categories':
        from .parser import CategoryParser
        category_parser = CategoryParser()
        categories = category_parser.retrieve_categories()
        try:
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
            print('Successfully parsed data and added to db', file=sys.stdout)

        except Exception as e:
            db.session.rollback()
            print('Error occured adding data: {}'.format(e), file=sys.stdout)
            sys.exit()
    else:
        raise NotImplementedError()
