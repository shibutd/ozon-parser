from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text

from app import db
from app.models import Category, Item, CategorySchema, ItemSchema
from .helpers import PaginationHelper


category_schema = CategorySchema()
items_wo_prices_schema = ItemSchema(exclude=('prices',))
item_schema = ItemSchema()

parser = reqparse.RequestParser()


class CategoryListResource(Resource):
    '''Represent API endpoint for categories.
    '''

    def get(self):
        categories = Category.query.filter(
            db.func.nlevel(Category.path) == 1).all()
        results = category_schema.dump(categories, many=True)
        return results


class ItemListResource(Resource):
    '''Represent API endpoint for list of items.
    '''

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'category',
            type=str,
            required=True,
            location='args',
            help='Required query parameter'
        )
        args = parser.parse_args()
        category_slug = args['category']

        # Get category
        category = Category.query.get_or_404(category_slug)

        # Get leaf categories, children of category from request
        sql_q = text(
            '''
            SELECT * FROM categories as f1
            WHERE NOT EXISTS (
                SELECT * FROM categories AS f2
                WHERE f1.path @> f2.path
                AND f1.path <> f2.path
            )
            AND path <@ :path
            '''
        )
        resultproxy = db.engine.execute(sql_q, {'path': category.slug})

        subcategories_slugs = [
            rowproxy['slug']
            for rowproxy in resultproxy
        ]

        # Get items referring to leaf categories
        items_query = Item.query.filter(
            Item.category_slug.in_(subcategories_slugs))

        pagination_helper = PaginationHelper(
            request,
            query=items_query,
            resource_for_url='api.itemlistresource',
            params={'category': category_slug},
            key_name='results',
            schema=items_wo_prices_schema
        )

        results = pagination_helper.paginate_query()

        return results


class ItemResource(Resource):
    '''Represent API endpoint for single item.
    '''

    def get(self, id):
        item = Item.query.options(
            joinedload('prices')).get_or_404(id)
        result = item_schema.dump(item)
        return result
