from unittest import TestCase

from flask import json, url_for

from app import create_app, db
from app.factories import (
    CategoryFactory, ItemFactory, PriceFactory)
from app.models import Item
from app.api import status


class TestViews(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('test')
        cls.test_client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    def setUp(self):
        db.create_all()
        # Creating fixtures
        # Creating categories level 1
        self.category1 = CategoryFactory.create(name='electronics')
        self.category2 = CategoryFactory.create(name='clothes')
        # Creating categories level 2
        category_lvl2_1 = CategoryFactory.create(
            name='tv', parent=self.category1)
        category_lvl2_2 = CategoryFactory.create(
            name='smartphone', parent=self.category1)
        # Creating categories level 3
        category_lvl3_1 = CategoryFactory.create(
            name='led-tv', parent=category_lvl2_1)
        category_lvl3_2 = CategoryFactory.create(
            name='oled-tv', parent=category_lvl2_1)
        # Creating items
        for category in [category_lvl2_2, category_lvl3_1, category_lvl3_2]:
            ItemFactory.create_batch(2, category_slug=category.slug)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_retrieve_categories_list(self):
        '''Ensure we can retrieve list of top level categories.
        '''
        response = self.test_client.get(
            url_for('api.categorylistresource', _external=True))
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]['name'], self.category1.name)
        self.assertEqual(response_data[1]['name'], self.category2.name)

    def test_retrieve_items_list_wo_category(self):
        '''Ensure we can't retrieve list of items without specifying
        the category.
        '''
        response = self.test_client.get(
            url_for(
                'api.itemlistresource',
                _external=True
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            response_data['message'],
            {'category': 'Required query parameter'}
        )

    def test_retrieve_items_list_with_category(self):
        '''Ensure we can retrieve list of items related to specific
        category.
        '''
        response = self.test_client.get(
            url_for(
                'api.itemlistresource',
                category=self.category1.slug,
                _external=True
            )
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['count'], 6)
        # Get page size from settings
        page_size = self.app.config.get('PAGINATION_PAGE_SIZE')
        self.assertEqual(len(response_data['results']), page_size)

        response = self.test_client.get(
            url_for(
                'api.itemlistresource',
                category=self.category2.slug,
                _external=True
            )
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['count'], 0)

    def test_pagination(self):
        '''Ensure pagination works as expected.
        '''
        url = url_for(
            'api.itemlistresource',
            category=self.category1.slug,
            _external=True
        )

        url_next = url_for(
            'api.itemlistresource',
            category=self.category1.slug,
            page=2,
            _external=True
        )

        url_prev = url_for(
            'api.itemlistresource',
            category=self.category1.slug,
            page=1,
            _external=True
        )

        response = self.test_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data['previous'], None)
        self.assertEqual(response_data['next'], url_next)

        response = self.test_client.get(url_next)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data['previous'], url_prev)
        self.assertEqual(response_data['next'], None)

    def test_retrieve_item_with_prices(self):
        '''Ensure we can retrieve specific item with its prices.
        '''
        item = Item.query.first()
        prices = PriceFactory.create_batch(3, item_id=item.id)

        response = self.test_client.get(
            url_for(
                'api.itemresource',
                id=9999,
                _external=True
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.test_client.get(
            url_for(
                'api.itemresource',
                id=item.id,
                _external=True
            )
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['name'], item.name)
        self.assertEqual(len(response_data['prices']), 3)
        self.assertEqual(
            response_data['prices'][0]['value'],
            prices[0].value
        )
        self.assertEqual(
            response_data['prices'][1]['value'],
            prices[1].value
        )
        self.assertEqual(
            response_data['prices'][2]['value'],
            prices[2].value
        )
