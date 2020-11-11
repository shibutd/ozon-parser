import os
import re
import time
import logging
from queue import PriorityQueue, Empty
from threading import Thread, Lock, Event
from pathlib import Path
from urllib.parse import urlparse, ParseResult
from contextvars import ContextVar
from typing import Tuple, List, Dict, Union, Iterable, Generator

from selenium import webdriver  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from fake_useragent import UserAgent  # type: ignore


var_driver = ContextVar('driver', default=None)


class ProducerThread(Thread):
    """Custom thread class for getting urls from queue, parsing it
    and updating items' list and maximum page number.
    Check the queue for a task after a specified period of time.
    """

    def __init__(
        self,
        queue: PriorityQueue,
        event: Event,
        parser: 'ItemsParser',
        url: str
    ) -> None:
        Thread.__init__(self)
        self.queue = queue
        self.start_event = event
        self.parser = parser
        self.url = url

    def run(self) -> None:
        while True:
            # Start and wait for event to start
            if not self.start_event.is_set():
                logging.debug('Producer: Waiting for start...')

            self.start_event.wait()
            logging.debug('Producer: Producing task to the queue')
            # Get current and max page number
            max_page_number = self.parser.max_page_number
            current_page_number = self.parser.current_page_number

            logging.debug('Producer: Current page: %s, max page: %s',
                          current_page_number, max_page_number)
            # If current page is equal to maximum page, stop
            if current_page_number == max_page_number:
                logging.debug('Producer: Finishing...')
                break
            # If not, add additional tasks to queue
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
            # Update current page number
            logging.debug('Producer: Added %s tasks to the queue', i)
            self.parser.update_current_page_number(max_page_number)
            # Wait for tasks to complete
            logging.debug('Producer: ')
            self.queue.join()


class ConsumerThread(Thread):
    """Custom thread class for getting urls from queue, parsing it
    and updating items' list and maximum page number.
    Ask the queue for a task after a specified period of time.
    """

    def __init__(
        self,
        queue: PriorityQueue,
        event: Event,
        parser: 'ItemsParser',
        check_period: int = 1
    ) -> None:
        Thread.__init__(self)
        self.queue = queue
        self.terminate_event = event
        self.parser = parser
        self.check_period = check_period

    def run(self) -> None:
        while True:
            # If terminate event is set, stop
            if self.terminate_event.is_set():
                logging.debug(
                    'Consumer %s: Terminate event is set. Finishing...',
                    self.name
                )
                break
            # Ask queue for task
            try:
                logging.debug('Consumer %s: Request item from queue',
                              self.name)
                queue_item = self.queue.get(block=False)
            # If it is empty wait
            except Empty:
                logging.debug('Consumer %s: Queue is empty, waiting...',
                              self.name)
                time.sleep(self.check_period)
            else:
                _, url = queue_item
                logging.debug('Consumer %s: Got item from queue^ %s',
                              self.name, url)
                # Parse url got from queue
                try:
                    items = self.parser.get_page_items(url)
                except Exception as e:
                    logging.debug(
                        'Consumer %s: Error occured while parsing %s: %s',
                        self.name, url, e
                    )
                    self.queue.task_done()
                    break
                # Refresh the general list of items with items
                # retrieved from the parsed URL
                self.parser.update_items(items)

                logging.debug('Consumer %s: Task Done: processed %s',
                              self.name, url)
                # Signal queue task is done
                self.queue.task_done()


class ItemsParser:
    """Class to retrieve item's name, external_url, image_url and price
    from category page. Uses selenium browser to load javascript content.
    Uses multithreading to parse several pages simultaneously.
    """
    WORKERS = os.cpu_count() or 1
    LOAD_PAGE_PAUSE_TIME = 7
    SCROLL_PAUSE_TIME = 1
    MAX_PAGE_WITH_LAZY_LOADING = 11

    def __init__(self) -> None:
        driver_path = Path(__file__).parent.parent.parent / 'chromedriver.exe'
        self.executable_path: Dict[str, str] = {
            'executable_path': driver_path.as_posix()
        }
        self.user_agent = UserAgent()
        self.all_items: List[Dict] = []
        self.max_page_number: int = 1
        self.current_page_number: int = 0
        self._items_lock = Lock()
        self._max_page_lock = Lock()
        self._current_page_lock = Lock()

    def get_browser(self, headless: bool = True) -> webdriver:
        """Create Selenium browser instance.
        """
        # Check context variable if browser is already created
        driver = var_driver.get()
        # If not - create and save to context variable
        if driver is None:
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('headless')
            options.add_argument('user_agent={}'.format(UserAgent().random))
            # Adding options to avoid accept certificate errors
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            driver = webdriver.Chrome(options=options, **self.executable_path)
            var_driver.set(driver)

        return driver

    def scroll_down_page(self, browser: webdriver) -> None:
        """Scroll page down to load javascript content.
        """
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(self.SCROLL_PAUSE_TIME)

    def get_max_page_number(self, soup) -> int:
        """Get maximum page number from loaded page.
        """
        page_tags = soup.find_all(href=re.compile(r'page=\d+$'))
        urls = set()
        # Find number of page in found tags
        for tag in page_tags:
            page_match = re.search(
                r'/category/\S+?page=(\d+)$',
                tag['href']
            )
            page_number = page_match.group(1) if page_match else 0
            # Add to set to get only unique ones
            urls.add(int(page_number))

        return max(urls) if urls else self.MAX_PAGE_WITH_LAZY_LOADING

    @staticmethod
    def get_item_external_url(tags: bs4.element.ResultSet) -> ParseResult:
        external_url = urlparse(tags[0]['href'])
        return external_url

    @staticmethod
    def get_item_name(tags: bs4.element.ResultSet) -> str:
        for tag in tags:
            text = tag.text
            if tag.contents and tag.contents[0] == text:
                return text
        return ''

    @staticmethod
    def get_item_price(tags: bs4.element.ResultSet):
        price_match = tags[1].find('span') or tags[-1].find('span')
        price = int(price_match.text.replace('\u2009', '')[:-1]) \
            if price_match else 0
        return price

    def process_tags(self, tags: bs4.element.ResultSet) -> List[Dict]:
        """Get items' list from found tags.
        """
        items = []
        for tag in tags:
            # Look for <a> tags with href containing 'context' or 'product'
            inner_tags = tag.find_all(href=re.compile('context')) \
                or tag.find_all(href=re.compile('product'))
            try:
                item = {}
                # Get item's external url
                external_url = self.get_item_external_url(inner_tags)
                item['external_url'] = external_url.path
                # Get item's image
                item['image_url'] = inner_tags[0].find('img')['src']
                # Get item's name, filter out some things
                name = self.get_item_name(inner_tags)
                if not name or (external_url.query and 'сертификат' in name):
                    continue
                item['name'] = name
                # Get item's price
                price = self.get_item_price(inner_tags)
                item['price'] = price

                items.append(item)

            except Exception:
                continue

        return items

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Union[str, int]]]:
        """Get items from page's html content.
        """
        tags_containers = soup.select('div.widget-search-result-container')
        if tags_containers:
            container = tags_containers[0]

            tags_for_page = container.find_all(
                style=re.compile('grid-column-start'))

            items_from_tags = self.process_tags(tags_for_page)
        else:
            items_from_tags = []

        return items_from_tags

    def get_page_items(self, url: str) -> List[Dict[str, Union[str, int]]]:
        """Get items for given url.
        """
        # Load browser, open url and wait content to load
        browser = self.get_browser(headless=False)
        time.sleep(0.01)
        browser.get(url)
        time.sleep(self.LOAD_PAGE_PAUSE_TIME)
        # Scroll browser's page down to load javascript content.
        self.scroll_down_page(browser)

        soup = BeautifulSoup(browser.page_source, 'lxml')
        # Get maximum page number from current page and update
        # for futher parsing.
        max_page_number = self.get_max_page_number(soup)
        self.update_max_page_number(max_page_number)

        items = self.parse(soup)
        return items

    @staticmethod
    def get_pages_urls(
        url: str,
        numbers: Iterable[int]
    ) -> Generator[Tuple[int, str], Tuple[str, Iterable[int]], None]:
        for page_number in numbers:
            yield page_number, '{0}?page={1}'.format(url, page_number)

    def update_max_page_number(
            self, page_number: int, force: bool = False) -> None:
        with self._max_page_lock:
            if page_number > self.max_page_number or force:
                self.max_page_number = page_number

    def update_current_page_number(self, page_number: int) -> None:
        with self._current_page_lock:
            self.current_page_number = page_number

    def update_items(self, items: List[Dict]) -> None:
        with self._items_lock:
            self.all_items.extend(items)

    def get_items(self, url: str) -> List[Dict]:
        self.all_items = []
        # Create queue for urls to parse, event to start parsing,
        # event to terminate parsing
        q: PriorityQueue = PriorityQueue()
        update_q_event: Event = Event()
        terminate_event: Event = Event()
        # Create thread to produce urls for queue
        producer_thread = ProducerThread(
            queue=q,
            event=update_q_event,
            parser=self,
            url=url
        )
        producer_thread.start()
        # Create threads to get urls from queue and parse
        consumer_threads = []

        for _ in range(self.WORKERS):
            consumer_thread = ConsumerThread(
                queue=q,
                event=terminate_event,
                parser=self
            )
            consumer_thread.start()
            consumer_threads.append(consumer_thread)
        # Update maximum and current page's number to start from 1
        logging.debug('Main thread: Starting session...')
        self.update_current_page_number(0)
        self.update_max_page_number(1, force=True)
        update_q_event.set()

        producer_thread.join()

        logging.debug('Main thread: Finishing session...')
        terminate_event.set()

        for t in consumer_threads:
            t.join()

        return self.all_items
