from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    adress = db.Column(db.String(64), unique=True)
    subcategories = db.relationship('Subcategory', backref='category')

    def __repr__(self):
        return '<Category %r>' % self.name


class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    adress = db.Column(db.String(64), unique=True)      
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    items = db.relationship('Item', backref='subcategory')

    def __repr__(self):
        return '<Subcategory %r>' % self.name


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    adress = db.Column(db.String(64), unique=True)
    price = db.Column(db.Text)
    image = db.Column(db.String(64))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'))


    def __repr__(self):
        return '<Items %r>' % self.name


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))