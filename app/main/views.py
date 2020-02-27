import re
from flask import render_template, redirect, url_for, session, flash
from . import main
from ..models import Category, Item
from ..plot_line import plot_line
from .forms import ItemForm


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


@main.context_processor
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


@main.route('/', methods=['GET', 'POST'])
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


@main.route('/item/<int:item_id>')
def item(item_id):
    adress_from_id = '/context/detail/id/' + str(item_id) + '/'
    obj = Item.query.filter_by(adress=adress_from_id).first_or_404()
    script, div, cdn_js = plot_line(obj.price)
    return render_template('item.html', script=script, div=div, cdn_js=cdn_js, item=obj)