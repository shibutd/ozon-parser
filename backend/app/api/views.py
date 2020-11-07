from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.orm import joinedload

from app.models import Category, Item, CategorySchema, ItemSchema
from .helpers import PaginationHelper


category_schema = CategorySchema()
items_wo_prices_schema = ItemSchema(exclude=('prices',))
item_schema = ItemSchema()

parser = reqparse.RequestParser()
parser.add_argument(
    'category',
    type=str,
    required=True,
    location='args',
    help='Required query parameter'
)


class CategoryListResource(Resource):
    '''API endpoint for list of categories that has no parents.
    '''

    def get(self):
        categories = Category.query.filter(
            Category.is_parent()).all()

        results = category_schema.dump(categories, many=True)
        return results


class SubcategoryListResource(Resource):
    '''API endpoint for list of categories that has no children.
    '''

    def get(self, slug):
        category = Category.query.get_or_404(slug)

        children_categories = Category.query.filter(
            Category.has_no_children(),
            Category.path.descendant_of(category.path)
        ).all()

        results = category_schema.dump(
            children_categories, many=True)
        return results


class ItemListResource(Resource):
    '''API endpoint for list of items.
    '''

    def get(self):
        args = parser.parse_args()
        category_slug = args['category']

        # Get category
        category = Category.query.get_or_404(category_slug)

        # Get items referred to categories without children
        items_query = Item.query.join(Category).filter(
            Category.has_no_children(),
            Category.path.descendant_of(category.path)
        )

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
    '''API endpoint for single item.
    '''

    def get(self, id):
        item = Item.query.options(
            joinedload('prices')).get_or_404(id)
        result = item_schema.dump(item)
        return result
