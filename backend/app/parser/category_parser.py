import re
import json
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, AsyncGenerator

import httpx
from bs4 import BeautifulSoup  # type: ignore
from fake_useragent import UserAgent  # type: ignore


class Fetcher:
    """Class to make asynchronous GET requests.
    """
    KEEPALIVE_CONNECTIONS: int = 5
    MAX_CONNECTIONS: int = 10
    TIMEOUT: int = 10

    def __init__(self):
        self.user_agent = UserAgent()

    async def fetch(self, session: httpx.AsyncClient,
                    url: str) -> Tuple[str, httpx.Response]:
        """Make asynchronous GET request to url.
        """
        headers = {'User-Agent': self.user_agent.random}
        try:
            response = await session.get(url, headers=headers)
            if response.status_code != 200:
                response.raise_for_status()
        except httpx.HTTPStatusError:
            logging.debug('Failed while parsing %s: status code %s',
                          url, response.status_code)
        except httpx.HTTPError as e:
            logging.debug('Failed while parsing %s: %s', url, e)
        return url, response

    def get_session(self) -> httpx.AsyncClient:
        """Return client for making asynchronous requests.
        """
        limits = httpx.Limits(
            max_keepalive_connections=self.KEEPALIVE_CONNECTIONS,
            max_connections=self.MAX_CONNECTIONS
        )
        session = httpx.AsyncClient(limits=limits, timeout=self.TIMEOUT)
        return session

    async def fetch_pages_content(self, urls: List[str]) -> AsyncGenerator:
        """Asyncroniously fetch and page's html content from urls.
        """
        tasks = []
        session = self.get_session()

        async with session:
            for url in urls:
                tasks.append(
                    asyncio.create_task(
                        self.fetch(session, url)
                    ))

            for task_result in asyncio.as_completed(tasks):
                fetched_content = await task_result
                url, response = fetched_content
                yield url, response.text


class ContentParser(Fetcher, ABC):
    """Class for parse page's html content.
    """

    async def get_pages_content(self, urls: List[str]) -> List[Dict]:
        """Asyncroniously get pages' html content and parse it.
        """
        pages_content = []

        data = [result async for result in self.fetch_pages_content(urls)]

        for url, page_html in data:
            page_content = self.parse(page_html)
            pages_content.append({url: page_content})

        return pages_content

    @abstractmethod
    def parse(self, page_html: str):
        """Abstract method for parsing html.
        """
        pass


class CategoryParser(ContentParser):
    """Class to get parent (from main page) categories' names and urls.
    """
    PATTERN: str = 'catalogMenu'

    def process_pattern(self, page_json: Dict) -> List[Dict[str, str]]:
        """Process dict of categories.
        """
        page_content = []

        for category in page_json['categories']:
            category_dict = {
                'name': category['title'],
                'url': category['url']
            }
            page_content.append(category_dict)

        return page_content

    def parse(self, page_html: str) -> List[Dict[str, str]]:
        """Find and process tag with given pattern,
        return list of categories.
        """
        soup = BeautifulSoup(page_html, 'lxml')

        tag = soup.find(id=re.compile(self.PATTERN))
        tag_content = tag['data-state']

        page_json = json.loads(tag_content)
        page_content = self.process_pattern(page_json)

        return page_content

    def get_categories(self, url: str) -> List[Dict[str, str]]:
        categories = asyncio.run(self.get_pages_content([url]))
        return categories


class SubcategoryParser(ContentParser):
    """Class to get non-parent categories' names and urls.
    """
    PATTERNS: List[str] = [
        'searchCategorySubtree',
        'catalogHorizontalMenu',
        'objectLine'
    ]

    def get_filtered_sections(
        self,
        sections: List[Dict[str, str]],
        obj_url: str
    ) -> List[Dict[str, str]]:
        """Filter out sections, leaving only those
        with unique url.
        """
        unique_urls = set()
        unique_urls.add(obj_url)

        new_sections = []

        for section in sections:
            url = section['url']

            if url in unique_urls:
                continue
            else:
                new_sections.append(section)
                unique_urls.add(url)

        return new_sections

    def process_subtree_pattern(
        self,
        page_json: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """Process dict of categories when pattern 'searchCategorySubtree'.
        """
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

    def process_horizontalmenu_pattern(
        self,
        page_json: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """Process dict of categories when pattern 'catalogHorizontalMenu'.
        """
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
                            'name': section['title'],
                            'url': section['url']
                        }

                        if section_dict['url'].startswith('/category'):
                            section_dict['name'].replace(' ', '')
                            section_dict['url'].replace(' ', '')

                            category_dict['sections'].append(section_dict)

                    page_content.append(category_dict)
            except KeyError:
                continue

        # Remove repeating values of 'sections'
        for obj in page_content:
            obj_url = obj['url']
            obj['sections'] = self.get_filtered_sections(
                obj['sections'], obj_url)

        return page_content

    def process_objectline_pattern(
        self,
        page_json: Dict[str, List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        """Process dict of categories when pattern 'objectLine'.
        """
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

    def parse(self, page_html: str) -> List[Dict]:
        """Find and process tag with given pattern,
        return list of categories.
        """
        soup = BeautifulSoup(page_html, 'lxml')
        # Trying to find out what pattern is using on page
        # Сonsequentially check each pattern
        # When pattern found, break
        for pattern in self.PATTERNS:
            tag = soup.find(id=re.compile(pattern))
            if tag:
                break
        else:
            return []

        tag_content = tag['data-state']
        page_json = json.loads(tag_content)

        # Get function for processing depending on found pattern
        process_functions = {
            'searchCategorySubtree': self.process_subtree_pattern,
            'catalogHorizontalMenu': self.process_horizontalmenu_pattern,
            'objectLine': self.process_objectline_pattern
        }

        function = process_functions[pattern]
        page_content = function(page_json)
        return page_content

    def get_subcategories(self, urls: List[str]) -> List[Dict]:
        subcategories = asyncio.run(self.get_pages_content(urls))
        return subcategories
