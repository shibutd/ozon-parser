import sys
import os
import json
from datetime import datetime
from urllib.parse import urlparse

from app.models import Category, Item, Price
from app.parser import Parser


class DatabaseSaver:
    """Class to interact with database."""

    def __init__(self, session):
        self.session = session

    def save_categories_to_database(self, categories, parent=None):
        """Save categories to database and children categories if
        exists.
        """
        category_objects = []
        children = []
        for category in categories:
            # Create Category object
            try:
                category_obj = Category(
                    name=category['name'],
                    url=category['url'],
                    parent=parent
                )
            except AttributeError:
                continue

            category_objects.append(category_obj)
            # Add children categories for further saving
            sections = category.get('sections')
            if sections:
                children.append((sections, category_obj))

        self.session.bulk_save_objects(category_objects)
        self.session.commit()
        # Save children categories
        for section_objs, parent_section_obj in children:
            self.save_categories_to_database(
                section_objs,
                parent_section_obj
            )

    def save_subcategories_to_database(
            self, all_subcategories, parent_categories):
        """Save subcategories corresponds to parent categories.
        """
        for category in parent_categories:
            subcategories = all_subcategories[category.url]
            self.save_categories_to_database(subcategories, category)

    def save_items_to_database(self, items, category):
        """Save items to database that corresponds to given
        category.
        """
        items_objects = []
        prices = []
        for item in items:
            # Create item object
            item_obj = Item(
                name=item['name'],
                url=item['external_url'],
                image_url=item['image_url'],
                category_slug=category.slug
            )
            items_objects.append(item_obj)
            # Add price dict for further insering to database
            prices.append(
                {
                    'value': item['price'],
                    'item_id': item_obj.id
                }
            )
        self.session.bulk_save_objects(items_objects)
        self.session.commit()

        # SAVE PRICES
        self.save_prices_to_database(prices)

    def save_prices_to_database(self, prices):
        """Save prices to database.
        """
        self.session.bulk_insert_mappings(Price, prices)
        self.session.commit()


class JsonSaveMixin:
    """Add functionality of saving to .json file."""

    @staticmethod
    def get_timestamp():
        return datetime.strftime(datetime.now(), '%H-%M_%d-%m-%Y')

    @staticmethod
    def create_directory(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            raise Exception(
                'Unable to create directory {0}: {1}'
                .format(path, e)
            )

    def save_to_jsonfile(self, name, data, path='.'):
        timestamp = self.get_timestamp()
        # If path was given, create directory
        if path != '.':
            self.create_directory(path)
        with open(
            '{0}/{1}_{2}.json'.format(path, name, timestamp),
            'w',
            encoding='utf-8'
        ) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class DataImporter:
    """Class for search and interact with .json files saved earlier.
    """

    def __init__(self, path):
        self.global_path = path

    def get_files_names(self, pattern):
        """Find .json files with corresponds to given pattern.
        """
        for file_path in self.global_path.glob(pattern):
            if file_path.suffix == '.json':
                yield file_path.as_posix()

    @staticmethod
    def get_data_from_file(file):
        """Load data from .json file.
        """
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data

    def get_data_from_multiple_files(self, pattern):
        for file in self.get_files_names(pattern):
            data = self.get_data_from_file(file)
            yield data


class UrlProcessMixin:
    """Add functionality to work with urls."""

    @staticmethod
    def get_full_url(base_url, path):
        return '{0}{1}'.format(base_url, path)

    @staticmethod
    def get_url_path(url):
        return urlparse(url).path


class ParserLaucher(JsonSaveMixin, UrlProcessMixin, DatabaseSaver):
    """Class to interact with Parser.
    """
    BASE_URL = 'https://www.ozon.ru'

    def __init__(
        self,
        result_save_directory,
        save_to_json=False,
        save_to_db=False,
        *args,
        **kwargs
    ):
        self.result_save_directory = result_save_directory
        self.save_to_json = save_to_json
        self.save_to_db = save_to_db
        super().__init__(*args, **kwargs)
        self.parser = Parser()

    @staticmethod
    def get_parent_categories_from_db():
        """Load categories with no parents.
        """
        return Category.query.filter(Category.is_parent()).all()

    def fetch_parent_categories(self):
        print('Fetching parent categories...', file=sys.stdout)
        # Parse site for parent categories
        categories = self.parser.get_parent_categories(self.BASE_URL)
        categories = categories[0][self.BASE_URL]

        # SAVE TO .JSON FILE
        if self.save_to_json:
            print('Saving to .json file...', file=sys.stdout)
            self.save_to_jsonfile(
                'parent_categories',
                categories,
                self.result_save_directory
            )

        # SAVE TO DATABASE
        if self.save_to_db:
            print('Saving to database...', file=sys.stdout)
            self.save_categories_to_database(categories)

    def fetch_subcategories(self):
        print('Fetching subcategories...', file=sys.stdout)
        # Get parent categories
        parent_categories = self.get_parent_categories_from_db()
        full_urls = [
            self.get_full_url(self.BASE_URL, parent_category.url)
            for parent_category in parent_categories
        ]
        subcategories = self.parser.get_subcategories(full_urls)

        merged_subcategories = {}
        for subcategory in subcategories:
            key = list(subcategory)[0]
            value = subcategory[key]
            merged_subcategories[self.get_url_path(key)] = value

        # SAVE TO .JSON FILE
        if self.save_to_json:
            print('Saving to .json file...', file=sys.stdout)
            self.save_to_jsonfile(
                'subcategories',
                merged_subcategories,
                self.result_save_directory
            )

        # SAVE TO DATABASE
        if self.save_to_db:
            print('Saving to database...', file=sys.stdout)
            self.save_subcategories_to_database(
                merged_subcategories,
                parent_categories
            )

    def fetch_items(self):
        print('Fetching items...', file=sys.stdout)
        # Get parent categories
        parent_categories = self.get_parent_categories_from_db()

        for parent_category in parent_categories:
            # For every parent category get its leaves categories
            leaf_categories = Category.query.filter(
                Category.has_no_children(),
                Category.path.descendant_of(parent_category.path)
            ).all()

            for leaf_category in leaf_categories:
                # For every leaf category get corresponding items
                print('Parsing category:', leaf_category.name,
                      file=sys.stdout)

                url = self.get_full_url(
                    self.BASE_URL,
                    leaf_category.url
                )
                items = self.parser.get_items(url)

                # SAVE ITEMS TO .JSON FILE
                if self.save_to_json:
                    print('Saving to .json file...', file=sys.stdout)
                    self.save_to_jsonfile(
                        'items_{}'.format(leaf_category.slug),
                        items,
                        self.result_save_directory
                    )

                # SAVE ITEMS TO DATABASE
                if self.save_to_db:
                    print('Saving to database...', file=sys.stdout)
                    self.save_items_to_database(items, leaf_category)
