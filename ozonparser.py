import re
import os
from flask import Flask, render_template, session, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired
from plot_line import plot_line
from parser1 import Parser
from apscheduler.schedulers.background import BackgroundScheduler 


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Пользователь', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ItemForm(FlaskForm):
    adress = StringField('Скопируйте сюда ссылку на товар: ')
    #name = StringField('Название товара: ')
    choice_category = SelectField('Выберите Категорию из списка: ', coerce=int)
    #choice_subcategory = SelectField('Выберите Подкатегорию: ', coerce=int)
    submit = SubmitField('Искать')


class ParseButton(FlaskForm):
   parse = SubmitField('Run Parser')


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


def best_prices(price_string):
    prices = price_string.split(' ')
    if prices[-1] != 'nan':
        price = int(prices[-1])
        prices = sorted([int(price) for price in prices if price != 'nan'])
        if len(prices) > 0:
            if len(prices) % 2 == 0:
                median = (prices[len(prices)//2] + prices[len(prices)//2 - 1]) / 2
            else:
                median = prices[len(prices)//2]
    else:
        return -100000
    return median - price


@app.context_processor
def utility_processor():
    def calculate_price(price_string, currency=u'₽'):
        price_pos = price_string.rfind(' ')
        price = price_string[price_pos+1:]
        if price == 'nan':
            return u'Товар не доступен'
        else:
            if len(price) > 3:
                return price[:-3] + ' ' + price[-3:] + ' ' + currency
            else:
                return price + ' ' + currency
    return dict(calculate_price=calculate_price)
    

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Category=Category, Subcategory=Subcategory, Item=Item)


@app.route('/', methods=['GET', 'POST'])
def index():
    category_list = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    category_list.insert(0, (0, ''))
    form = ItemForm()
    form.choice_category.choices = category_list
    if form.validate_on_submit():
        session['adress'] = form.adress.data
        session['choice'] = form.choice_category.data

        if session['adress'] == '' and session['choice'] == 0:
            flash('Необходимо ввести данные')
            return redirect(url_for('index'))

        elif session['adress'] == '' and session['choice'] != 0:
            category = Category.query.filter_by(id=session['choice']).first()
            session['choice'] = category.name
            items = Item.query.filter_by(category_id=category.id).all()
            items = [{'id': item.id, 'best_price': best_prices(item.price)} for item in items]
            items = sorted(items, key=lambda k: k['best_price'], reverse=True)[:5]
            best_items = [item.get('id') for item in items]
            items = Item.query.filter(Item.id.in_(best_items)).all()
            session['items'] = [{'name': item.name, 'price': item.price, \
                                 'adress': item.adress, 'image': item.image, \
                                 'id': re.search('\d+', str(item.adress)).group(0)} for item in items]
            return redirect(url_for('index'))

        elif session['adress'] != '':
            try:
                adress = re.search('id/\d+', str(session['adress'])).group(0)
            except:
                flash('Неверный формат, попробуйте еще раз')
                return redirect(url_for('index'))
            adress = '/context/detail/' + adress + '/'
            item = Item.query.filter_by(adress=adress).first()
            if item is None:
                flash('Извините, товар не найден')
                return redirect(url_for('index'))
            else:
                id = re.search('\d+', str(item.adress)).group(0)
                return redirect(url_for('item', item_id=id))
       
        else:
            return redirect(url_for('index'))
    return render_template('index.html', form=form, items=session.pop('items', None))


@app.route('/item/<int:item_id>')
def item(item_id):
    adress_from_id = '/context/detail/id/' + str(item_id) + '/'
    obj = Item.query.filter_by(adress=adress_from_id).first_or_404()
    script, div, cdn_js = plot_line(obj.price)
    return render_template('item.html', script=script, div=div, cdn_js=cdn_js, item=obj)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


#@app.route('/admin', methods=['GET', 'POST'])
#@login_required
def admin():
    #button = ParseButton()
    #if button.validate_on_submit():
    p = Parser()
    categories = p.get_categories()
    for category in categories[3:4]: ###
        category_ = Category.query.filter_by(adress=category.get('Adress')).first()
        if category_ is None:
            category_ = Category(name=category.get('Name'), adress=category.get('Adress'))
            db.session.add(category_)
            db.session.commit()
        subcategories = p.get_subcategories(category.get('Adress'))
        for subcategory in subcategories[:4]: ###
            subcategory_ = Subcategory.query.filter_by(adress=subcategory.get('Adress')).first()
            if subcategory_ is None:
                subcategory_ = Subcategory(name=subcategory.get('Name'), \
                                        adress=subcategory.get('Adress'), \
                                        category_id=category_.id)
                db.session.add(subcategory_)
                db.session.commit()
            items = p.get_items(subcategory.get('Adress'))
            for item in items:
                item_ = Item.query.filter_by(adress=item.get('Adress')).first()
                if item_ is None:

                    item_ = Item(name=item.get('Name'), \
                                 adress=item.get('Adress'), \
                                 price=str(item.get('Price')), \
                                 image=item.get('Image'), \
                                 category_id=category_.id, \
                                 subcategory_id=subcategory_.id)
                    db.session.add(item_)
                    db.session.commit()
                else:
                    item_.price = item_.price + ' ' + str(item.get('Price'))
                    db.session.add(item_)
                    db.session.commit()
    #return render_template('admin.html', form=button)


#if __name__ == '__main__':
#    app.run()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(admin, 'interval', minutes=720)
    scheduler.start()
    app.run()
