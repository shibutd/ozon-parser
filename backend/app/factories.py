import factory
import factory.fuzzy
from app import db
from .models import Category, Subcategory, Item, Price


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Category
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Category {}'.format(n))
    url = factory.Sequence(
        lambda n: 'http://category-{}'.format(n))


class SubcategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Subcategory
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Subcategory {}'.format(n))
    url = factory.Sequence(
        lambda n: 'http://subcategory-{}'.format(n))
    category_id = factory.SubFactory(CategoryFactory)


class ItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Item
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Subcategory {}'.format(n))
    external_id = factory.Sequence(
        lambda n: '{0}{1}{2}'.format(n, n + 1, n + 2))
    subcategory_id = factory.SubFactory(SubcategoryFactory)


class PriceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Price
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    value = factory.fuzzy.FuzzyDecimal(10.0, 100.0, 2)
    item_id = factory.SubFactory(ItemFactory)
