from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.sql import expression
from sqlalchemy.orm import joinedload
from sqlalchemy_utils.types.ltree import LQUERY
from app import db
from app.models import Category, Item, CategorySchema, ItemSchema
from .helpers import PaginationHelper


category_schema = CategorySchema()
items_wo_prices_schema = ItemSchema(exclude=('prices',))
item_schema = ItemSchema()

parser = reqparse.RequestParser()


class CategoryListResource(Resource):

    def get(self):
        categories = Category.query.filter(
            db.func.nlevel(Category.path) == 1).all()
        results = category_schema.dump(categories, many=True)
        return results


class ItemListResource(Resource):

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

        category = Category.query.get_or_404(category_slug)

        query = '%s.*{1}' % (category.slug)
        lquery = expression.cast(query, LQUERY)

        subcategories = Category.query.filter(
            Category.path.lquery(lquery)).all()
        subcategories_slugs = [
            subcategory.slug for subcategory in subcategories
        ]

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

    def get(self, id):
        item = Item.query.options(
            joinedload('prices')).get_or_404(id)
        result = item_schema.dump(item)
        return result
