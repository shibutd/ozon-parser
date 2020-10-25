import sys
import json
from datetime import datetime
from collections import Counter

import click
from flask import Blueprint

from app import db
from app.models import Category, Item, Price
from app.parser import Parser


cmd_bp = Blueprint('cmd', __name__)


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
        click.echo('File not found: {}'.format(path))
        sys.exit()

    click.echo('Importing data...')

    c = Counter()

    try:
        create_categories(loaded_json, counter=c)
    except Exception as e:
        db.session.rollback()
        click.echo('Error occured while importing data: {}'.format(e))
        sys.exit()

    db.session.commit()

    click.echo(
        "Categories processed={0} (created={1})".format(
            c["categories"], c["categories_created"]))
    click.echo(
        "Items processed={0} (created={1})".format(
            c["items"], c["items_created"]))


@cmd_bp.cli.command()
@click.option('-p', '--parse',
              type=click.Choice(
                  ['categories', 'subcategories', 'items'],
                  case_sensitive=False
              ),
              help='Parser type.',
              required=True)
@click.option('-j', '--json',
              is_flag=True,
              help='Save parsing result to .json file.')
def launch_parser(parse, json):
    """Parse data from 'ozon.ru' and save to db and .json file."""
    launcher = ParserLaucher(json)

    launcher_functions = {
        'categories': launcher.get_and_create_parent_categories,
        'subcategories': launcher.get_and_create_subcategories,
        'items': launcher.get_and_create_items
    }
    try:
        launcher_functions[parse]()
    except Exception as e:
        db.session.rollback()
        click.echo('Error occured while adding data: {}'.format(e))
        sys.exit()

    click.echo('Successfully parsed data and saved to database.')


class ParserLaucher:
    BASE_URL = 'https://ozon.ru'

    def __init__(self, save_to_json=False):
        self.save_to_json = save_to_json
        self.parser = Parser()

    @staticmethod
    def get_timestamp():
        return datetime.strftime(datetime.now(), '%H-%M_%d-%m-%Y')

    def get_url(self, url):
        return '{0}{1}'.format(self.BASE_URL, url)

    def save_to_jsonfile(self, name, data):
        print('Saving to .json file...', file=sys.stdout)
        timestamp = self.get_timestamp()
        with open(
            '{0}_{1}.json'.format(name, timestamp),
            'w',
            encoding='utf-8'
        ) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def get_parent_categories_from_db():
        return Category.query.filter(Category.is_parent()).all()

    def save_categories_to_database(self, categories, parent=None):
        category_objects = []
        children = []
        for category in categories:
            try:
                category_obj = Category(
                    name=category['name'],
                    url=category['url'],
                    parent=parent
                )
            except AttributeError:
                continue

            category_objects.append(category_obj)

            sections = category.get('sections')
            if sections:
                children.append((sections, category_obj))

        db.session.bulk_save_objects(category_objects)
        db.session.commit()

        for section_objs, parent_section_obj in children:
            self.save_categories_to_database(
                section_objs, parent_section_obj)

    def get_and_create_parent_categories(self):
        print('Getting parent categories...', file=sys.stdout)

        # Parse site for parent categories
        categories = self.parser.get_parent_categories(self.BASE_URL)
        categories = categories[0][self.BASE_URL]

        # SAVE TO .JSON FILE
        if self.save_to_json:
            self.save_to_jsonfile('parent_categories', categories)

        # SAVE TO DATABASE
        print('Saving to database...', file=sys.stdout)
        self.save_categories_to_database(categories)

    def get_and_create_subcategories(self):
        print('Getting subcategories...', file=sys.stdout)
        # Get parent categories
        parent_categories = self.get_parent_categories_from_db()

        urls = [self.get_url(parent_category.url)
                for parent_category in parent_categories]
        subcategories = self.parser.get_subcategories(urls)

        # SAVE TO .JSON FILE
        if self.save_to_json:
            self.save_to_jsonfile('subcategories', subcategories)

        # Convert from list of dictionaries to single dictionary
        merged_subcategories = {}
        for subcategory in subcategories:
            merged_subcategories.update(subcategory)

        print('Saving to database...', file=sys.stdout)
        for parent_category, url in zip(parent_categories, urls):
            children = merged_subcategories[url]
            self.save_categories_to_database(children, parent_category)

    def save_items_to_database(self, items, category):
        items_objects = []
        prices = []
        for item in items:
            item_obj = Item(
                name=item['name'],
                url=item['external_url'],
                image_url=item['image_url'],
                category=category
            )
            items_objects.append(item_obj)
            # Add price dict for further insering to database
            prices.append(
                {
                    'value': item['price'],
                    'item_id': item_obj.id
                }
            )
        db.session.bulk_save_objects(items_objects)
        db.session.commit()

        # SAVE PRICES TO DATABASE
        self.save_prices_to_database(prices)

    def save_prices_to_database(self, prices):
        db.session.bulk_insert_mappings(Price, prices)
        db.session.commit()

    def get_and_create_items(self):
        print('Getting items...', file=sys.stdout)
        # Get parent categories
        parent_categories = self.get_parent_categories_from_db()

        for parent_category in parent_categories:
            leaf_categories = Category.query.filter(
                Category.has_no_children(),
                Category.path.descendant_of(parent_category.path)
            ).all()

            for leaf_category in leaf_categories:
                print('Parsing category:', leaf_category.name,
                      file=sys.stdout)

                url = self.get_url(leaf_category.url)
                for idx, items in enumerate(
                        self.parser.get_items(url), 1):

                    # SAVE TO .JSON FILE
                    if self.save_to_json:
                        self.save_to_jsonfile(
                            'items_{0}_{1}'.format(leaf_category.slug, idx),
                            items
                        )

                    # SAVE ITEMS TO DB
                    self.save_items_to_database(items, leaf_category)
