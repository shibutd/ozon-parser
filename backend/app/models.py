import re
import datetime
from sqlalchemy.orm import remote, foreign
from sqlalchemy_utils import LtreeType, Ltree
from marshmallow import fields
from flask_marshmallow import Marshmallow
from app import db


ma = Marshmallow()


class Category(db.Model):
    __tablename__ = 'categories'

    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(64), primary_key=True)
    url = db.Column(db.String(64), unique=True, nullable=False)
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
            slug = re.search('/category/(\D+)-\d+', url).group(1)
            slug = slug.replace('-', '_')
            kwargs['slug'] = slug
        else:
            slug = kwargs.get('slug')
        ltree_slug = Ltree(slug)
        parent = kwargs.get('parent')
        kwargs['path'] = ltree_slug if not parent else parent.path + ltree_slug
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Category %r>' % self.name


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    external_id = db.Column(db.Integer, unique=True)
    image_url = db.Column(db.String(64))
    category_slug = db.Column(
        db.String(64), db.ForeignKey('categories.slug', ondelete='CASCADE'),
        nullable=False
    )
    category = db.relationship(
        'Category',
        backref=db.backref('items', lazy='dynamic', order_by='Item.id')
    )
    prices = db.relationship('Price', backref='item', lazy=True)

    def __repr__(self):
        return '<Item %r>' % self.name


class Price(db.Model):
    __tablename__ = 'prices'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(
        db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None))
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
    external_id = fields.Integer(required=True)
    image_url = fields.String(required=True)
    prices = fields.Nested('PriceSchema', many=True)
    _link = ma.URLFor('api.itemresource', id='<id>')


class PriceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Price
