import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re

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
        print(source)

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
                    item['Name'] = tag.find('span', {'data-test-id': 'tile-name'}).text.replace('\n', '').strip()
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
                #print(item)
                if item['Name'] and item['Price'] and item['Image'] and item['Adress']:
                    items_added += 1
                    if item.get('Price') > 5000:
                        items.append(item)
            if items_added == 0 or page_num == 1000:
                break
            else:
                page_num += 1
        return items

