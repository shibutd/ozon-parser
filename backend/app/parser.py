import os
import re
import json
import time
import asyncio
import logging
from queue import PriorityQueue, Empty
from threading import Thread, Lock, Event
from abc import ABC, abstractmethod
from pathlib import Path
from contextvars import ContextVar
from typing import Tuple, List, Dict, AsyncGenerator

import httpx
from selenium import webdriver  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from fake_useragent import UserAgent  # type: ignore


logging.basicConfig(filename='parser.log', filemode='w', level=logging.DEBUG)
# threadLocal = threading.local()
var_driver = ContextVar('driver', default=None)


class Fetcher:
    '''Class to make asynchronous get requests.
    '''
    KEEPALIVE_CONNECTIONS = 5
    MAX_CONNECTIONS = 10

    def __init__(self):
        self.user_agent = UserAgent()

    async def fetch(self, session: httpx.AsyncClient,
                    url: str) -> Tuple[str, httpx.Response]:
        '''Make GET request to url.
        '''
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
        limits = httpx.Limits(
            max_keepalive_connections=self.KEEPALIVE_CONNECTIONS,
            max_connections=self.MAX_CONNECTIONS
        )
        session = httpx.AsyncClient(limits=limits, timeout=10)
        return session

    async def fetch_pages_content(self, urls: List[str]) -> AsyncGenerator:
        '''Fetch html content from page.
        '''
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

    async def get_pages_content(self, urls: List[str]) -> List[Dict]:
        pages_content = []

        data = [result async for result in self.fetch_pages_content(urls)]

        for url, page_html in data:
            page_content = self.parse(page_html)
            pages_content.append({url: page_content})

        return pages_content

    @abstractmethod
    def parse(self, page_html: str):
        pass


class CategoryParser(ContentParser):
    '''Class to get parent (from main page) categories names and urls.
    '''
    PATTERN = 'catalogMenu'

    def process_pattern(self, page_json: Dict) -> List[Dict]:
        page_content = []

        for category in page_json['categories']:
            category_dict = {
                'name': category['title'].replace('\xa0', ' '),
                'url': category['url']
            }
            page_content.append(category_dict)

        return page_content

    def parse(self, page_html: str) -> List[Dict]:
        soup = BeautifulSoup(page_html, 'lxml')

        tag = soup.find(id=re.compile(self.PATTERN))
        tag_content = tag['data-state']

        page_json = json.loads(tag_content)
        page_content = self.process_pattern(page_json)

        return page_content

    def get_categories(self, url: str) -> List[Dict]:
        categories = asyncio.run(self.get_pages_content([url]))
        return categories


class SubcategoryParser(ContentParser):
    '''Class to get non-parent categories names and urls.
    '''
    PATTERNS = [
        'searchCategorySubtree',
        'catalogHorizontalMenu',
        'objectLine'
    ]

    def process_subtree_pattern(self, page_json: Dict) -> List[Dict]:
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
    def process_name(name: str) -> str:
        idx = name.find('по')
        if idx != -1:
            return name[:idx - 1]
        return name

    def filter_sections(self, obj: Dict) -> List[Dict]:
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

    def process_horizontalmenu_pattern(self, page_json: Dict) -> List[Dict]:
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

    def process_objectline_pattern(self, page_json: Dict) -> List[Dict]:
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

    def get_subcategories(self, urls: List[str]) -> List[Dict]:
        subcategories = asyncio.run(self.get_pages_content(urls))
        return subcategories


class ProducerThread(Thread):

    def __init__(self, queue, event, parser, url):
        super().__init__(self)
        self.queue = queue
        self.event = event
        self.parser = parser
        self.url = url

    def run(self):
        while True:
            if not self.event.is_set():
                logging.debug('Producer thread: Waiting for start...')

            self.event.wait()
            logging.debug('Producer thread: Producing task to the queue')

            # while current_page_number < max_page_number:
            max_page_number = self.parser.max_page_number
            current_page_number = self.parser.current_page_number

            logging.debug('Producer thread: Current page: %s, max page: %s',
                          current_page_number, max_page_number)

            if current_page_number == max_page_number:
                logging.debug('Producer thread: Finishing...')
                break

            i = 0
            for page_number, url in self.parser.get_pages_urls(
                self.url,
                range(
                    current_page_number + 1,
                    max_page_number + 1
                )
            ):
                i += 1
                self.queue.put((page_number, url))

            logging.debug('Producer thread: Added %s tasks to the queue', i)
            self.parser.update_current_page_number(max_page_number)

            logging.debug('Producer thread: ')
            self.queue.join()
            # current_page_number = max_page_number

            # if last_processed_page_number == max_page_number:
            #     break


class ConsumerThread(Thread):

    def __init__(self, queue, parser, check_period=1):
        super().__init__(self)
        self.queue = queue
        # self.event = event
        self.parser = parser
        self.check_period = check_period

    def run(self):
        while True:
            try:
                logging.debug('Consumer thread %s: Request item from queue',
                              self.name)
                queue_item = self.queue.get(block=False)
            except Empty:
                logging.debug('Consumer thread %s: Queue is empty, waiting...',
                              self.name)
                time.sleep(self.check_period)
            else:
                if queue_item is None:
                    logging.debug(
                        'Consumer thread %s: Got "None" from queue. Finishing...',
                        self.name
                    )
                    break
                _, url = queue_item
                logging.debug('Consumer thread %s: Got item from queue^ %s',
                              self.name, url)
                items = self.parser.get_page_items(url)

                self.parser.update_items(items)
                # self.parser.update_current_page_number(page_number)

                logging.debug('Consumer thread %s: Task Done: processed %s',
                              self.name, url)
                self.queue.task_done()
            # if terminate_event.is_set():
            #     break


class ItemsParser:
    '''Class to retrieve item's name, external_url, image_url and price
    from category page. Uses selenium browser to load javascript content.
    Uses multithreading for several page parsing simultaneously.
    '''
    WORKERS = os.cpu_count()
    LOAD_PAGE_PAUSE_TIME = 7
    SCROLL_PAUSE_TIME = 3
    MAX_SIZE_ITEMS_TRANSITION = 1000
    MAX_PAGE_WITH_LAZY_LOADING = 11

    def __init__(self):
        driver_path = Path(__file__).parent.parent / 'chromedriver.exe'
        self.executable_path = {'executable_path': str(driver_path)}
        self.user_agent = UserAgent()
        self.all_items = []
        self._items_lock = Lock()
        self._max_page_lock = Lock()
        self._current_page_lock = Lock()

    def get_browser(self, headless=True):
        # driver = getattr(threadLocal, 'driver', None)
        driver = var_driver.get()
        if driver is None:
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('headless')
            options.add_argument('user_agent={}'.format(UserAgent().random))
            driver = webdriver.Chrome(options=options, **self.executable_path)
            # setattr(threadLocal, 'driver', driver)
            var_driver.set(driver)

        return driver

    def scroll_down_page(self, browser):
        '''Scroll page down until all javascript content is loaded.
        '''
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

    def get_max_page_number(self, soup):
        page_tags = soup.find_all(href=re.compile(r'page=\d+$'))
        urls = set()

        for tag in page_tags:
            page_number = re.search(
                r'/category/\S+?page=(\d+)$',
                tag['href']
            ).group(1)
            urls.add(int(page_number))

        return max(urls) if urls else self.MAX_PAGE_WITH_LAZY_LOADING

    # @staticmethod
    # def get_item_external_url(tags):
    #     return

    @staticmethod
    def get_item_name(tags):
        for tag in tags:
            name = tag.text
            if name[0].isdigit() or name[0] == ' ':
                continue
            else:
                return name
        return ''

    @staticmethod
    def get_item_price(tags):
        price = tags[1].find('span') or tags[-1].find('span')
        return int(price.text.replace('\u2009', '')[:-1])

    def process_tags(self, tags):
        items = []
        for tag in tags:
            inner_tags = tag.find_all(href=re.compile('context')) \
                or tag.find_all(href=re.compile('product'))
            try:
                item = {}

                external_url = inner_tags[0]['href']
                if not external_url.endswith('/'):
                    continue

                item['external_url'] = external_url
                item['image_url'] = inner_tags[0].find('img')['src']
                item['name'] = self.get_item_name(inner_tags)
                if not item['name']:
                    continue

                item['price'] = self.get_item_price(inner_tags)

                items.append(item)

            except Exception:
                continue

        return items

    def parse(self, soup):
        tags_container = soup.select('div.widget-search-result-container')[0]

        tags_for_page = tags_container.find_all(
            style=re.compile('grid-column-start'))

        items_from_tags = self.process_tags(tags_for_page)
        return items_from_tags

    def get_page_items(self, url):
        browser = self.get_browser(headless=False)
        browser.get(url)
        time.sleep(self.LOAD_PAGE_PAUSE_TIME)

        # self.scroll_down_page(browser)
        soup = BeautifulSoup(browser.page_source, 'lxml')

        max_page_number = self.get_max_page_number(soup)
        self.update_max_page_number(max_page_number)

        items = self.parse(soup)
        return items

    @staticmethod
    def get_pages_urls(url, numbers):
        for page_number in numbers:
            yield page_number, '{0}?page={1}'.format(url, page_number)

    def update_max_page_number(self, page_number):
        with self._max_page_lock:
            if page_number > self.max_page_number:
                self.max_page_number = page_number
            # event.set()

    def update_current_page_number(self, page_number):
        with self._current_page_lock:
            self.current_page_number = page_number

    def update_items(self, items):
        with self._items_lock:
            self.all_items.extend(items)
            if len(self.all_items) > self.MAX_SIZE_ITEMS_TRANSITION:
                yield self.all_items
                self.all_items = []

        # yield self.all_items

    def get_items(self, url):
        self.all_items = []
        # self.max_page_number = 5
        # self.current_page_number = 0

        q = PriorityQueue()
        update_q_event = Event()

        producer_thread = ProducerThread(
            queue=q,
            event=update_q_event,
            parser=self,
            url=url
        )
        producer_thread.start()

        consumer_threads = []
        workers_number = self.WORKERS if self.WORKERS else 1
        for _ in range(workers_number):
            consumer_thread = ConsumerThread(
                queue=q,
                parser=self
            )
            consumer_thread.start()
            consumer_threads.append(consumer_thread)

        logging.debug('Main thread: Starting...')
        self.update_current_page_number(0)
        self.update_max_page_number(1)
        update_q_event.set()

        producer_thread.join()

        logging.debug('Main thread: Finishing session...')
        for _ in range(workers_number):
            q.put(None)

        for t in consumer_threads:
            t.join()

        return self.all_items


class Parser:
    def __init__(self):
        self.category_parser = CategoryParser()
        self.subcategory_parser = SubcategoryParser()
        self.items_parser = ItemsParser()

    def get_parent_categories(self, url):
        return self.category_parser.get_categories(url)

    def get_subcategories(self, urls):
        return self.subcategory_parser.get_subcategories(urls)

    def get_items(self, url):
        return self.items_parser.get_items(url)
