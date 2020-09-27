import re
import json
from abc import ABC, abstractmethod
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

    async def fetch_pages_content(self, links):
        tasks = []
        limits = httpx.Limits(max_keepalive=5, max_connections=10)

        async with httpx.AsyncClient(limits=limits) as session:
            for link in links:
                tasks.append(
                    asyncio.create_task(
                        self.fetch(session, link)
                    ))

            tags = []
            for task_result in asyncio.as_completed(tasks):
                fetched_content = await task_result
                url, response = fetched_content
                page_content = self.parse(response.text)

                tags.append({url: page_content})

            return tags

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

    def parse(self, page_content):
        soup = BeautifulSoup(page_content, 'lxml')

        tag = soup.find(id=re.compile(self.PATTERN))
        tag_content = tag['data-state']
        page_json = json.loads(tag_content)

        page_content = self.process_pattern(page_json)
        return page_content

    async def retrieve_categories(self):
        # Retrieve categories
        urls = [self.BASE_URL]
        categories = await self.fetch_pages_content(urls)

        return categories


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

    def process_horizontalmenu_pattern(self, page_json):
        page_content = []

        for category in page_json['categories']:
            if 'section' in category and 'url' in category and \
                    category['url'].startswith('/category'):

                category_dict = {
                    'name': category['title'].capitalize(),
                    'url': category['url'],
                    'sections': []
                }

                for section in category['section']:
                    if 'title' in section and 'url' in section and \
                            section['title'].replace(' ', '') and \
                            section['url'].replace(' ', '') and \
                            section['url'].startswith('/category'):

                        category_dict['sections'].append(
                            {
                                'name': section['title'].replace('\xa0', ' '),
                                'url': section['url']
                            }
                        )

                page_content.append(category_dict)

        # remove repeating values of 'sections'
        for item in page_content:
            sections = item['sections']

            values = {item['url'] for item in sections}
            if len(sections) > len(values):
                sections_temp = []
                for item in sections:
                    if item['url'] in values:
                        values.remove(item['url'])

                        name = item['name']
                        idx = name.find('по')
                        if idx != -1:
                            item['name'] = name[:idx - 1]

                    sections_temp.append(item)

            sections = sections_temp

        return page_content

    def process_objectline_pattern(self, page_json):
        page_content = []

        for category in page_json['items']:
            if 'title' in category and 'link' in category:
                category_dict = {
                    'name': category['title'],
                    'url': category['link']
                }
                page_content.append(category_dict)

        return page_content

    def parse(self, page_content):
        soup = BeautifulSoup(page_content, 'lxml')

        for pattern in self.PATTERNS:
            tag = soup.find(id=re.compile(pattern))
            if tag:
                break
        else:
            return []

        tag_content = tag['data-state']
        page_json = json.loads(tag_content)

        if pattern == 'searchCategorySubtree':
            page_content = self.process_subtree_pattern(page_json)
        elif pattern == 'catalogHorizontalMenu':
            page_content = self.process_horizontalmenu_pattern(page_json)
        else:  # pattern == 'objectLine'
            page_content = self.process_objectline_pattern(page_json)

        return page_content

    async def retrieve_subcategories(self, urls):
        # Retrieve subcategories

        def get_url(url):
            return '{0}{1}'.format(self.BASE_URL, url)

        full_urls = [get_url(url) for url in urls]
        subcategories = await self.fetch_pages_content(full_urls)

        return subcategories
