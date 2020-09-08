import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from . import db
from .models import Category, Subcategory, Item


class Parser:
    def __init__(self):
        self.ua = UserAgent()
        self.source = 'http://ozon.ru'
        self.categories = list()

    def get_soup(self, source=None):
        if source is None:
            source = self.source
        else:
            source = self.source + source
        r = requests.get(source, headers={'User-Agent': self.ua.random})
        c = r.content
        return BeautifulSoup(c, 'html.parser')

    def get_categories(self):
        soup = self.get_soup()
        all = soup.find_all(href=re.compile('category'))
        for tag in all:
            category = dict()
            try:
                category['Name'] = tag.find('span').text.replace('\n', '').strip()
            except:
                category['Name'] = None
            category['Adress'] = re.search('/category/.*\d{4,5}/', str(tag)).group(0)
            if category['Name'] and category['Adress'] and \
            category['Adress'] not in [d.get('Adress') for d in self.categories]:
                self.categories.append(category)
        return self.categories

    def get_subcategories(self, category):
        soup = self.get_soup(source=category)
        all = soup.find_all(href=re.compile('category'))
        subcategories = list()
        for tag in all:
            subcategory = dict()
            try:
                subcategory['Adress'] = re.search('/category/.*-\d{4,5}/', str(tag)).group(0)
                subcategory['Name'] = re.search('[a-z-]+-\d', subcategory.get('Adress')).group(0)[:-2]
            except:
                subcategory['Adress'] = None
                subcategory['Name'] = None
            if subcategory['Adress'] and \
            subcategory['Adress'] not in [d.get('Adress') for d in self.categories] and \
            subcategory['Adress'] not in [d.get('Adress') for d in subcategories]:
                print(subcategory)
                subcategories.append(subcategory)
        return subcategories

    def get_items(self, subcategory):
        page_num = 1
        items = list()
        while True:
            soup = self.get_soup(source=subcategory + f'?page={page_num}')
            all = soup.find_all(href=re.compile('context'))
            for tag in all:
                items_added = 0
                item = dict()
                try:
                    item['Name'] = tag.find('span', {'data-test-id': 'tile-name'}).\
                    text.replace('\n', '').strip()
                except:
                    item['Name'] = None
                try:
                    item['Price'] = tag.find('span', {'data-test-id': 'tile-price'}).text.replace('\n', '').replace(u'\u2009', '').strip()[:-1]
                    item['Price'] = int(item['Price'])
                except:
                    item['Price'] = float('nan')
                try:
                    img = tag.find('img')
                    item['Image'] = re.search('http.*jpg"', str(img)).group(0)[:-1]
                except:
                    item['Image'] = None
                try:
                    item['Adress'] = re.search('/context/detail/id/\d+/', str(tag)).group(0)
                except:
                    item['Adress'] = None
                if item['Name'] and item['Price'] and item['Image'] and item['Adress']:
                    print(item)
                    items_added += 1
                    if item.get('Price') > 10000:
                        print('added')
                        items.append(item)
            if items_added == 0 or page_num == 1000:
                break
            else:
                page_num += 1
        return items


def launch_parser():
    parser = Parser()
    categories = parser.get_categories()
    for category in categories[:2]: ###
        category_ = Category.query.filter_by(adress=category.get('Adress')).first()
        if category_ is None:
            category_ = Category(name=category.get('Name'), adress=category.get('Adress'))
            db.session.add(category_)
            db.session.commit()
        subcategories = parser.get_subcategories(category.get('Adress'))
        for subcategory in subcategories: ###
            subcategory_ = Subcategory.query.filter_by(adress=subcategory.get('Adress')).first()
            if subcategory_ is None:
                subcategory_ = Subcategory(name=subcategory.get('Name'), \
                                        adress=subcategory.get('Adress'), \
                                        category_id=category_.id)
                db.session.add(subcategory_)
                db.session.commit()
            items = parser.get_items(subcategory.get('Adress'))
            for item in items:
                item_ = Item.query.filter_by(adress=item.get('Adress')).first()
                if item_ is None:
                    item_ = Item(name=item.get('Name'), 
                        adress=item.get('Adress'), 
                        price=str(item.get('Price')),
                        image=item.get('Image'),
                        category_id=category_.id, 
                        subcategory_id=subcategory_.id)
                    db.session.add(item_)
                    db.session.commit()
                else:
                    item_.price = item_.price + ' ' + str(item.get('Price'))
                    db.session.add(item_)
                    db.session.commit()
