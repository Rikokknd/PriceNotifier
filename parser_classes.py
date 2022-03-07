import requests
from bs4 import BeautifulSoup
import re

# my libs
from data_structures import ParsedItem
from lib import log


class GeneralParser:
    _html: str
    _main_soup: BeautifulSoup
    _items: list

    def __init__(self, link):
        """Получает ссылку на страницу, которую нужно обработать(ссылки хранятся в конфиге).
                Последовательно вызывает нужные методы."""

        def get_html(url, params=None):
            result = requests.get(url, headers={
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
    'accept': '*/*'
}, params=params)
            return result.text if result.status_code == 200 else self.stop()

        self._link = link
        self._html = get_html(link)
        self._main_soup = BeautifulSoup(self._html, 'html.parser')
        self._items = []
        self._next_page = None
        self.parse_html()
        self.save_items()
        self.stop()

    def parse_html(self):
        pass
        # Реализуется в суб-парсерах

    def save_items(self):
        """Сохраняет элементы в БД."""
        for item in self._items:
            if item is None:
                continue
            # проверяем, есть ли элемент в таблице. Вызываем save или update
            if item.check_link_existence_in_source_table():
                item.update_item()
            else:
                item.save_new_item()

    def stop(self):
        if self._next_page and self._items:
            log.info("Переход на следующую страницу...")
            print(self._next_page)
            self.__class__(self._next_page)
        del self


class ParseTTT(GeneralParser):

    _site = 'ttt'

    def parse_html(self):
        """Обрабатывает страницу, сохраняет полученные элементы в массив items.
        Если у открытой страницы есть продолжение, сохраняет ссылку на следующую страницу."""
        def get_item(soup: BeautifulSoup):
            """возвращает объект ParsedItem"""
            soup = soup.find('div', class_='product-details')
            item_name_raw = soup.find('a').get_text()
            item_name = re.sub(r'\\+', '/', item_name_raw)
            item_link = soup.find('a')['href']
            item_price_span = soup.find('span', class_='price')
            item_price_raw = item_price_span.find('ins').get_text() if item_price_span.find('ins') else item_price_span.get_text()
            item_price = int(''.join(i for i in item_price_raw if i.isdigit()))
            return ParsedItem(self._site, item_name.replace("'", '"'), item_link, item_price)

        def get_link_to_next_page(soup: BeautifulSoup) -> str or None:
            next_page = soup.find('a', class_='next page-numbers')
            return next_page if not next_page else next_page['href']
        
        list_of_item_soups = self._main_soup.findAll('li', class_='type-product')
        for item in list_of_item_soups:
            self._items.append(get_item(item))

        self._next_page = get_link_to_next_page(self._main_soup)


class ParseMobiTech(GeneralParser):

    _site = 'mobitech'
    _prefix = 'https://www.mobiteh.net'

    def parse_html(self):
        """Обрабатывает страницу, сохраняет полученные элементы в массив items.
        Если у открытой страницы есть продолжение, сохраняет ссылку на следующую страницу."""

        def get_item(soup):
            """возвращает объект ParsedItem"""
            # soup = soup.find('form', class_='product_brief_block')
            item_name_raw = soup.find('div', class_='prdbrief_name').find('a').get_text()
            item_name = re.sub(r'\\+', '/', item_name_raw)
            item_link_raw = soup.find('div', class_='prdbrief_name').find('a')['href']
            item_link = self._prefix + item_link_raw
            item_price = int(soup.find('input', class_='product_price')['value'])
            if item_price == 0:
                return None
            return ParsedItem(self._site, item_name.replace("'", '"'), item_link, item_price)

        def get_link_to_next_page(soup: BeautifulSoup) -> str or None:
            next_page = soup.find('a', string=re.compile('след '))
            return next_page if not next_page else self._prefix + next_page['href']

        list_of_item_soups = self._main_soup.findAll('form', class_='product_brief_block')
        for item_html_block in list_of_item_soups:
            item = get_item(item_html_block)
            if item:
                self._items.append(item)

        self._next_page = get_link_to_next_page(self._main_soup)


class ParseFoks(GeneralParser):
    _site = 'foks'

    def parse_html(self):
        """Обрабатывает страницу, сохраняет полученные элементы в массив items.
        Если у открытой страницы есть продолжение, сохраняет ссылку на следующую страницу."""

        def get_item(soup: BeautifulSoup):
            """возвращает объект ParsedItem"""
            item_name_raw = soup.find('span', class_='content-title').get_text()
            item_name = re.sub(r'\\+', '/', item_name_raw.replace("'", '"'))
            item_link = soup.get('href')
            item_price_span = soup.find('span', class_='lower-current').get_text()
            item_price = int(''.join(i for i in item_price_span if i.isdigit()))
            item_available = False if soup.find('div', class_='button_disabled') else True
            if not item_available:
                return None
            return ParsedItem(self._site, item_name, item_link, item_price)

        def get_link_to_next_page(soup: BeautifulSoup) -> str or None:
            next_page = soup.find('a', class_='indicate_next')
            return (re.sub(r'\?.+', '', self._link) + next_page['href']) if next_page else None

        list_of_item_soups = self._main_soup.findAll('a', class_='product-unit')
        for item in list_of_item_soups:
            self._items.append(get_item(item))

        self._next_page = get_link_to_next_page(self._main_soup)


class ParseDonSmart(GeneralParser):
    _site = 'donbass_smart'

    def parse_html(self):
        """Обрабатывает страницу, сохраняет полученные элементы в массив items.
        Если у открытой страницы есть продолжение, сохраняет ссылку на следующую страницу."""

        def get_item(soup: BeautifulSoup):
            """возвращает объект ParsedItem"""
            item_name_raw = soup.find('div', class_="product-name").a.get_text()
            item_name = re.sub(r'\\+', '/', item_name_raw.replace("'", '"'))
            item_link = "http://donbass-smart.ru" + soup.find('div', class_="product-name").a['href']
            item_price_span = soup.find('li', class_='product-price').get_text()
            item_price = int(''.join(i for i in item_price_span if i.isdigit()))
            item_available = False if 'disabled' in soup.find('button').attrs else True
            if not item_available:
                return None
            return ParsedItem(self._site, item_name, item_link, item_price)

        # def get_link_to_next_page(soup: BeautifulSoup) -> str or None:
        #     next_page = soup.find('a', class_='indicate_next')
        #     return (re.sub(r'\?.+', '', self._link) + next_page['href']) if next_page else None

        list_of_item_soups = self._main_soup.findAll('form', class_='shop2-product-item')
        for item in list_of_item_soups:
            self._items.append(get_item(item))

        # self._next_page = get_link_to_next_page(self._main_soup)