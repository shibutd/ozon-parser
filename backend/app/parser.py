from abc import ABC, abstractmethod
import re
import json
import asyncio
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Parser(ABC):
    BASE_URL = 'https://ozon.ru'

    def __init__(self):
        self.user_agent = UserAgent()

    async def fetch(self, session, url):
        headers = {'User-Agent': self.user_agent.random}
        response = await session.get(url, headers=headers)
        return url, response

    async def fetch_pages_content(self, urls):
        tasks = []
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)

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

    def retrieve_categories(self):
        # Retrieve categories
        urls = [self.BASE_URL]

        categories = asyncio.run(self.fetch_pages_content(urls))

        return categories[0][self.BASE_URL]


class SubcategoryParser(Parser):
    PATTERNS = ['searchCategorySubtree', 'catalogHorizontalMenu', 'objectLine']

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
                        'url': '/category/{}'.format(section['info']['urlValue'])
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
        return section

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

        pattern_function = {
            'searchCategorySubtree': self.process_subtree_pattern,
            'catalogHorizontalMenu': self.process_horizontalmenu_pattern,
            'objectLine': self.process_objectline_pattern
        }

        function = pattern_function[pattern]
        page_content = function(page_json)
        return page_content

    async def retrieve_subcategories(self, urls):
        # Retrieve subcategories
        def get_url(url):
            return '{0}{1}'.format(self.BASE_URL, url)

        full_urls = [get_url(url) for url in urls]
        subcategories = await self.fetch_pages_content(full_urls)

        return subcategories
