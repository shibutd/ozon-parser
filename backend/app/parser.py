import re
import json
import time
import asyncio
import concurrent.futures
from abc import ABC, abstractmethod
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Parser(ABC):

    def __init__(self):
        self.user_agent = UserAgent()

    async def fetch(self, session, url):
        headers = {'User-Agent': self.user_agent.random}
        response = await session.get(url, headers=headers)
        return url, response

    async def fetch_pages_content(self, urls):
        tasks = []
        limits = httpx.Limits(max_keepalive_connections=5,
                              max_connections=10)

        async with httpx.AsyncClient(limits=limits) as session:
            for url in urls:
                tasks.append(
                    asyncio.create_task(
                        self.fetch(session, url)
                    ))

            pages_content = []
            for task_result in asyncio.as_completed(tasks):
                fetched_content = await task_result
                url, response = fetched_content
                page_content = self.parse(response.text)

                pages_content.append({url: page_content})

            return pages_content

    @abstractmethod
    def parse(self, page_content):
        pass


class CategoryParser(Parser):
    PATTERN = 'catalogMenu'

    def process_pattern(self, page_json):
        page_content = []

        for category in page_json['categories']:
            category_dict = {
                'name': category['title'].replace('\xa0', ' '),
                'url': category['url']
            }
            page_content.append(category_dict)

        return page_content

    def parse(self, page_html):
        soup = BeautifulSoup(page_html, 'lxml')

        tag = soup.find(id=re.compile(self.PATTERN))
        tag_content = tag['data-state']

        page_json = json.loads(tag_content)
        page_content = self.process_pattern(page_json)

        return page_content

    def retrieve_categories(self, url):
        # Retrieve categories
        categories = asyncio.run(self.fetch_pages_content([url]))
        return categories


class SubcategoryParser(Parser):
    PATTERNS = [
        'searchCategorySubtree',
        'catalogHorizontalMenu',
        'objectLine'
    ]

    def process_subtree_pattern(self, page_json):
        page_content = []

        for category in page_json['categories'][0]['categories']:
            category_dict = {
                'name': category['info']['name'].capitalize(),
                'url': '/category/{}'.format(category['info']['urlValue']),
                'sections': []
            }

            for section in category['categories']:
                category_dict['sections'].append(
                    {
                        'name': section['info']['name'],
                        'url': '/category/{}'.format(
                            section['info']['urlValue'])
                    }
                )

            page_content.append(category_dict)

        return page_content

    @staticmethod
    def process_name(name):
        idx = name.find('по')
        if idx != -1:
            return name[:idx - 1]
        return name

    def filter_sections(self, obj):
        sections = obj['sections']
        unique_urls = set(section['url'] for section in sections)

        if len(sections) > len(unique_urls):
            new_sections = []

            for section in sections:
                url = section['url']
                if url in unique_urls:
                    unique_urls.remove(url)

                    name = self.process_name(section['name'])
                    section['name'] = name

                new_sections.append(section)
            return new_sections
        return sections

    def process_horizontalmenu_pattern(self, page_json):
        page_content = []

        for category in page_json['categories']:
            try:
                if category['url'].startswith('/category'):
                    category_dict = {
                        'name': category['title'].capitalize(),
                        'url': category['url'],
                        'sections': []
                    }

                    for section in category['section']:
                        section_dict = {
                            'name': section['title'].replace('\xa0', ' '),
                            'url': section['url']
                        }

                        if section_dict['url'].startswith('/category'):
                            section_dict['name'].replace(' ', '')
                            section_dict['url'].replace(' ', '')

                            category_dict['sections'].append(section_dict)

                    page_content.append(category_dict)
            except KeyError:
                continue

        # remove repeating values of 'sections'
        for obj in page_content:
            obj['sections'] = self.filter_sections(obj)

        return page_content

    def process_objectline_pattern(self, page_json):
        page_content = []

        for category in page_json['items']:
            try:
                category_dict = {
                    'name': category['title'],
                    'url': category['link']
                }
                page_content.append(category_dict)
            except KeyError:
                continue

        return page_content

    def parse(self, page_html):
        soup = BeautifulSoup(page_html, 'lxml')

        for pattern in self.PATTERNS:
            tag = soup.find(id=re.compile(pattern))
            if tag:
                break
        else:
            return []

        tag_content = tag['data-state']
        page_json = json.loads(tag_content)

        process_functions = {
            'searchCategorySubtree': self.process_subtree_pattern,
            'catalogHorizontalMenu': self.process_horizontalmenu_pattern,
            'objectLine': self.process_objectline_pattern
        }

        function = process_functions[pattern]
        page_content = function(page_json)
        return page_content

    def retrieve_subcategories(self, urls):
        # Retrieve subcategories
        subcategories = asyncio.run(self.fetch_pages_content(urls))
        return subcategories


class ItemsParser(Parser):
    LOAD_PAGE_PAUSE_TIME = 5
    SCROLL_PAUSE_TIME = 3
    WORKERS = 5
    MAX_PAGE_NUMBER = 100

    def __init__(self):
        driver_path = Path(__file__).parent.parent / 'chromedriver.exe'
        self.executable_path = {'executable_path': str(driver_path)}
        self.user_agent = UserAgent()

    def get_browser(self):
        browser = None
        return browser

    def scroll_down_page(self, browser):
        # Get scroll height
        last_height = browser.execute_script(
            "return document.body.scrollHeight")

        while True:
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(self.SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_page_items(self, url):
        browser = self.get_browser()
        browser.visit(url)
        time.sleep(self.LOAD_PAGE_PAUSE_TIME)

        self.scroll_down_page(browser)

        items = self.parse(browser.html)
        return items

    def process_tags(tags):
        items = []
        for tag in tags:
            inner_tags = tag.find_all(href=re.compile('context')) \
                or tag.find_all(href=re.compile('product'))
            try:
                item = {}
                item['external_url'] = inner_tags[0]['href']

                img = inner_tags[0].find('img')
                item['image_url'] = img['src']

                item['name'] = inner_tags[1].text

                price = inner_tags[-1].find('span')
                item['price'] = int(price.text.replace('\u2009', '')[:-1])

                items.append(item)

            except Exception:
                continue

        return items

    def parse(self, page_html):
        soup = BeautifulSoup(page_html, 'lxml')
        tags_containers = soup.select('div.widget-search-result-container')

        tags_for_page = []
        for tags_container in tags_containers:
            for style in ['grid-column-start:span 12;background-color:;',
                          'grid-column-start: span 12;']:
                tags = tags_container.find_all('div', attrs={'style': style})
                tags_for_page.extend(tags)

        items_from_tags = self.process_tags(tags_for_page)
        return items_from_tags

    def retrive_items(self, url):

        def get_pages_urls(url, max_page_number):
            urls = ['{0}?page={1}'.format(url, page)
                    for page in range(1, max_page_number, 10)]
            return urls

        urls = get_pages_urls(url, self.MAX_PAGE_NUMBER)

        # i = 1
        all_items = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.WORKERS) as executor:
            for url in urls:
                futures.append(
                    executor.submit(self.get_page_items, url)
                )

        for future in concurrent.futures.as_completed(futures):
            items = future.result()
            all_items.extend(items)

            if len(all_items) > 1000:
                yield all_items
                all_items = []

        yield all_items
