from unittest import TestCase
from sqlalchemy_utils import Ltree

from app import create_app, db
from app.models import Category, Item
from app.factories import CategoryFactory


class TestModels(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('test')
        cls.test_client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_create_category(self):
        '''Ensure creating categories behave as expected.
        '''
        category1 = Category(
            name='First category',
            url='/category/cat-256121'
        )
        category2 = Category(
            name='Second category',
            url='/category/cat-two-256121',
            parent=category1
        )

        self.assertEqual(category1.slug, 'cat')
        self.assertEqual(category1.parent, None)
        self.assertEqual(category1.path, Ltree('cat'))
        self.assertEqual(category2.slug, 'cat_two')
        self.assertEqual(category2.parent, category1)
        self.assertEqual(category2.path, Ltree('cat.cat_two'))

    def test_create_item(self):
        '''Ensure creating items behave as expected.
        '''
        category = Category(
            name='First category',
            url='/category/cat-256121'
        )
        item = Item(
            name='Item',
            url='/context/id/21131/',
            category=category
        )

        self.assertEqual(item.id, '21131')

    def test_insert_ignore(self):
        '''Ensure inserting query ignores on conflict.
        '''
        category1 = Category(
            name='First category',
            url='/category/cat-256121'
        )
        category2 = Category(
            name='Second category',
            url='/category/cat-two-256121',
        )
        db.session.bulk_save_objects([category1, category2])

        category3 = Category(
            name='Third category',
            url='/category/cat-three-256121',
        )
        db.session.bulk_save_objects(
            [category1, category2, category3])

        categories_len = Category.query.count()
        self.assertEqual(categories_len, 3)

    def test_is_parent(self):
        '''Ensure is_parent method works as expected.
        '''
        category1 = CategoryFactory.create(name='electronics')
        CategoryFactory.create(name='tv', parent=category1)

        categories = Category.query.filter(
            Category.is_parent()).all()

        self.assertEqual(len(categories), 1)
        self.assertIn(category1, categories)

    def test_has_no_children(self):
        '''Ensure has_no_children method works as expected.
        '''
        category1 = CategoryFactory.create(name='electronics')
        category2 = CategoryFactory.create(
            name='tv', parent=category1)

        categories = Category.query.filter(
            Category.has_no_children()).all()

        self.assertEqual(len(categories), 1)
        self.assertIn(category2, categories)
