from decimal import Decimal
from unittest import TestCase
from flask import json, url_for, request
from app import create_app, db
from app.factories import (
    CategoryFactory, SubcategoryFactory, ItemFactory, PriceFactory)
from app.models import Category, CategorySchema
from app.api import status, helpers


class ViewsTests(TestCase):

    def setUp(self):
        self.app = create_app('test')
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Creating fixtures
        self.categories = CategoryFactory.create_batch(2)
        self.subcategories = SubcategoryFactory.create_batch(
            2, category_id=self.categories[0].id)
        self.items = ItemFactory.create_batch(
            6, subcategory_id=self.subcategories[0].id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_retrieve_categories_list(self):
        category1, category2 = self.categories

        response = self.test_client.get(
            url_for('api.categorylistresource', _external=True))
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]['name'], category1.name)
        self.assertEqual(response_data[1]['name'], category2.name)

    def test_retrieve_subcategories_list(self):
        category = self.categories[0]
        subcategory1, subcategory2 = self.subcategories

        response = self.test_client.get(
            url_for(
                'api.subcategorylistresource',
                _external=True
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            response_data['message'],
            {'category': 'Required query parameter'}
        )

        response = self.test_client.get(
            url_for(
                'api.subcategorylistresource',
                category=category.id,
                _external=True
            )
        )
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]['name'], subcategory1.name)
        self.assertEqual(response_data[1]['name'], subcategory2.name)

    def test_retrieve_items_list(self):
        subcategory = self.subcategories[0]
        item1, item2 = self.items[:2]

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
            {'subcategory': 'Required query parameter'}
        )

        response = self.test_client.get(
            url_for(
                'api.itemlistresource',
                subcategory=subcategory.id,
                _external=True
            )
        )
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['count'], 6)
        self.assertEqual(len(response_data['results']), 5)
        self.assertEqual(response_data['results'][0]['name'], item1.name)
        self.assertEqual(response_data['results'][1]['name'], item2.name)

    def test_pagination(self):
        subcategory = self.subcategories[0]

        url = url_for(
            'api.itemlistresource',
            subcategory=subcategory.id,
            _external=True
        )

        url_next = url_for(
            'api.itemlistresource',
            subcategory=subcategory.id,
            page=2,
            _external=True
        )
        url_prev = url_for(
            'api.itemlistresource',
            subcategory=subcategory.id,
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

    def test_retrieve_items(self):
        item = self.items[0]
        prices = PriceFactory.create_batch(3, item_id=item.id)

        response = self.test_client.get(
            url_for(
                'api.itemresource',
                id=1000,
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
            Decimal(str(response_data['prices'][0]['value'])),
            prices[0].value
        )


class HelpersTests(TestCase):

    def setUp(self):
        self.app = create_app('test')
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.test_request_context = self.app.test_request_context()
        self.app_context.push()
        self.test_request_context.push()
        db.create_all()

        CategoryFactory.create_batch(6)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_pagination_helper(self):
        query = Category.query
        schema = CategorySchema()
        per_page = 5
        page_name = 'page'

        pagination_helper = helpers.PaginationHelper(
            request,
            query=query,
            resource_for_url='api.categorylistresource',
            params={},
            key_name='results',
            schema=schema
        )

        self.assertEqual(pagination_helper.request, request)
        self.assertEqual(pagination_helper.query, query)
        self.assertEqual(
            pagination_helper.resource_for_url,
            'api.categorylistresource'
        )
        self.assertEqual(pagination_helper.params, {})
        self.assertEqual(pagination_helper.key_name, 'results')
        self.assertEqual(pagination_helper.schema, schema)
        self.assertEqual(
            pagination_helper.results_per_page, per_page)
        self.assertEqual(
            pagination_helper.page_argument_name, page_name)

        results = pagination_helper.paginate_query()

        paginated_object = query.paginate(
            1, per_page, error_out=False)

        self.assertEqual(
            results['results'],
            schema.dump(paginated_object.items, many=True)
        )
        self.assertFalse(paginated_object.has_prev)
        self.assertEqual(results['previous'], None)

        self.assertTrue(paginated_object.has_next)
        self.assertEqual(
            results['next'],
            url_for('api.categorylistresource', page=2, _external=True)
        )
        self.assertEqual(results['count'], query.count())
