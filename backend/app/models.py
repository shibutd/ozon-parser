import re
import datetime

from sqlalchemy.orm import remote, foreign, aliased
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import exists, and_
from sqlalchemy.sql.expression import Insert
from sqlalchemy_utils import LtreeType, Ltree
from marshmallow import fields
from flask_marshmallow import Marshmallow

from app import db


ma = Marshmallow()


@compiles(Insert)
def insert_ignore(insert_stmt, compiler, **kwargs):
    '''Convert every SQL insert statement to insert_ignore:
    INSERT INTO test (id, bar) VALUES (1, 'a')
    becomes:
    INSERT INTO test (id, bar) VALUES (1, 'a') ON CONFLICT(foo) DO NOTHING
    '''
    insert = compiler.visit_insert(insert_stmt, **kwargs)
    if 'RETURNING' not in insert:
        ondup = 'ON CONFLICT DO NOTHING'
        insert = ' '.join((insert, ondup))
    return insert


# MODELS

class Category(db.Model):
    __tablename__ = 'categories'

    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), primary_key=True)
    url = db.Column(db.String(128), unique=True, nullable=False)
    path = db.Column(LtreeType, nullable=False)
    parent = db.relationship(
        'Category',
        primaryjoin=remote(path) == foreign(db.func.subpath(path, 0, -1)),
        backref='children',
        sync_backref=False,
        viewonly=True
    )

    __table_args__ = (
        db.Index('ix_categories_path', path, postgresql_using='gist'),
    )

    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            url = kwargs.get('url')
            slug = re.search(r'/category/(\D+)-\d+', url).group(1)
            slug = slug.replace('-', '_')
            kwargs['slug'] = slug
        else:
            slug = kwargs.get('slug')
        ltree_slug = Ltree(slug)
        parent = kwargs.get('parent')
        kwargs['path'] = ltree_slug if not parent else parent.path + ltree_slug
        super().__init__(*args, **kwargs)

    @classmethod
    def is_parent(cls):
        return db.func.nlevel(cls.path) == 1

    @classmethod
    def has_no_children(cls):
        c2 = aliased(Category)
        return ~exists().where(
            and_(cls.path.ancestor_of(c2.path), cls.path != c2.path))

    def __repr__(self):
        return '<Category %r>' % self.name


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(128), unique=True, nullable=False)
    image_url = db.Column(db.String(128))
    category_slug = db.Column(
        db.String(64), db.ForeignKey('categories.slug', ondelete='CASCADE'),
        nullable=False
    )
    category = db.relationship(
        'Category',
        backref=db.backref('items', lazy='dynamic', order_by='Item.id')
    )
    prices = db.relationship('Price', backref='item', lazy=True)

    def __init__(self, *args, **kwargs):
        if 'id' not in kwargs:
            url = kwargs.get('url')
            id = re.search(r'^\/.+[\/-](\d+)\/$', url).group(1)
            kwargs['id'] = id
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Item %r>' % self.name


class Price(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    date = db.Column(
        db.Date(),
        default=datetime.datetime.now,
        nullable=False
    )
    item_id = db.Column(
        db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'),
        nullable=False
    )

    def __repr__(self):
        return '<Price %r>' % self.value


# SCHEMAS

class CategorySchema(ma.Schema):
    name = fields.String(required=True)
    slug = fields.String(required=True)
    url = fields.String(required=True)


class ItemSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    url = fields.String(required=True)
    image_url = fields.String(required=True)
    prices = fields.Nested('PriceSchema', many=True)
    _link = ma.URLFor('api.itemresource', id='<id>')


class PriceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Price

    value = ma.auto_field()
    date = ma.auto_field()
