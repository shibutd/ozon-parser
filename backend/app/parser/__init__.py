import os
import logging
from typing import List, Dict

from .category_parser import CategoryParser, SubcategoryParser
from .items_parser import ItemsParser


log_filename = 'logs/parser.log'
os.makedirs(os.path.dirname(log_filename), exist_ok=True)

logging.basicConfig(
    filename=log_filename,
    filemode='w',
    level=logging.DEBUG
)


class Parser:
    def __init__(self) -> None:
        self.category_parser = CategoryParser()
        self.subcategory_parser = SubcategoryParser()
        self.items_parser = ItemsParser()

    def get_parent_categories(self, url: str) -> List[Dict]:
        return self.category_parser.get_categories(url)

    def get_subcategories(self, urls: List[str]) -> List[Dict]:
        return self.subcategory_parser.get_subcategories(urls)

    def get_items(self, url: str) -> List[Dict]:
        return self.items_parser.get_items(url)
