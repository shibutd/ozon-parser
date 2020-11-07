from flask import Blueprint
from flask_restful import Api
from .views import (CategoryListResource, SubcategoryListResource,
                    ItemListResource, ItemResource)


api_bp = Blueprint('api', __name__)
api = Api(api_bp)


api.add_resource(CategoryListResource, '/categories')
api.add_resource(SubcategoryListResource, '/subcategories/<string:slug>')
api.add_resource(ItemListResource, '/items')
api.add_resource(ItemResource, '/items/<int:id>')
