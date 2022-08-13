# external libs
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re
# my libs

def scratch_parse(link):
    def get_html(url, params=None):
            result = requests.get(url, headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                'accept': '*/*'}, params=params)
            return result.text

    def get_item(soup: BeautifulSoup):
            soup = soup.find('div', class_='product-details')
            item_name_raw = soup.find('a').get_text()
            item_name = re.sub(r'\\+', '/', item_name_raw)
            item_link = soup.find('a')['href']
            item_price_span = soup.find('span', class_='price')
            item_price_raw = item_price_span.find('ins').get_text() if item_price_span.find('ins') else item_price_span.get_text()
            item_price = int(''.join(i for i in item_price_raw if i.isdigit()))
            return (item_name.replace("'", '"'), item_link, item_price)


    main_soup = BeautifulSoup(get_html(link), 'html.parser')
    items = []

    list_of_item_soups = main_soup.findAll('li', class_='type-product')
    
    for item in list_of_item_soups:
        items.append(get_item(item))

    pprint(items)

if __name__ == '__main__':
    links = [
            "https://ttt.dn.ua/product-category/smartfony/",
            "https://ttt.dn.ua/product-category/watch-fitness-bracelet/",
            "https://ttt.dn.ua/product-category/accesories-xiaomi/",
            "https://ttt.dn.ua/product-category/naushniki/"
        ]
    URL = links[3]
    scratch_parse(URL)