import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from . import db


ma = Marshmallow()


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    url = db.Column(db.String(64), unique=True)
    subcategories = db.relationship(
        'Subcategory',
        backref='category',
        lazy=True
    )

    def __repr__(self):
        return '<Category %r>' % self.name


class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    url = db.Column(db.String(64), unique=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'),
        nullable=False
    )
    items = db.relationship('Item', lazy=True)

    def __repr__(self):
        return '<Subcategory %r>' % self.name


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    external_id = db.Column(db.String(64), unique=True)
    image_url = db.Column(db.String(64))
    subcategory_id = db.Column(
        db.Integer, db.ForeignKey('subcategories.id', ondelete='CASCADE'),
        nullable=False
    )
    prices = db.relationship('Price', backref='category', lazy=True)

    def __repr__(self):
        return '<Item %r>' % self.name


class Price(db.Model):
    __tablename__ = 'prices'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(
        db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None))
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

class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category


class SubcategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Subcategory


class ItemSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    external_id = fields.String(required=True)
    image_url = fields.String(required=True)
    prices = fields.Nested('PriceSchema', many=True)
    _link = ma.URLFor('api.itemresource', id='<id>')


class PriceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Price
