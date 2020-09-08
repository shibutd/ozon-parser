from flask import request
from flask_restful import Resource, reqparse
from app.models import (Category, Subcategory, Item,
                        CategorySchema, SubcategorySchema, ItemSchema)
from .helpers import PaginationHelper


category_schema = CategorySchema()
subcategory_schema = SubcategorySchema()
items_wo_prices_schema = ItemSchema(exclude=('prices',))
item_schema = ItemSchema()

parser = reqparse.RequestParser()


class CategoryListResource(Resource):

    def get(self):
        categories = Category.query.all()
        results = category_schema.dump(categories, many=True)
        return results


class SubcategoryListResource(Resource):

    def get(self):
        parser.add_argument(
            'category',
            type=int,
            required=True,
            location='args',
            help='Required query parameter'
        )
        args = parser.parse_args()

        subcategories = Subcategory.query.filter_by(
            category_id=args['category']).all()

        results = subcategory_schema.dump(subcategories, many=True)
        return results


class ItemListResource(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'subcategory',
            type=int,
            required=True,
            location='args',
            help='Required query parameter'
        )
        args = parser.parse_args()
        subcategory_id = args['subcategory']

        items_query = Item.query.filter_by(
            subcategory_id=subcategory_id)

        pagination_helper = PaginationHelper(
            request,
            query=items_query,
            resource_for_url='api.itemlistresource',
            params={'subcategory': subcategory_id},
            key_name='results',
            schema=items_wo_prices_schema
        )

        results = pagination_helper.paginate_query()
        return results


class ItemResource(Resource):

    def get(self, id):
        item = Item.query.get_or_404(id)
        result = item_schema.dump(item)
        return result
