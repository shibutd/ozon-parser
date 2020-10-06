import factory
import factory.fuzzy

from app import db
from .models import Category, Item, Price


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Category
        sqlalchemy_session = db.session

    url = factory.LazyAttribute(
        lambda obj: '/category/{}-22521'.format(obj.name))


class ItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Item
        sqlalchemy_session = db.session

    name = factory.Sequence(lambda n: 'Item %d' % n)
    url = factory.Sequence(
        lambda n: '/context/detail/id/%04d/' % n)
    category_slug = factory.SubFactory(CategoryFactory)


class PriceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Price
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    item_id = factory.SubFactory(ItemFactory)
