# external libs
import requests
# my libs
from read_config import read_parameters, read_json
import lib
import parser_classes


def parse(site: dict):
    """Принимает словарь с параметрами"""
    parsers = {"ParseTTT": parser_classes.ParseTTT,
               "ParseMobiTech": parser_classes.ParseMobiTech,
               "ParseFoks": parser_classes.ParseFoks,
               "ParseDonSmart": parser_classes.ParseDonSmart}

    def check_site(url):
        result = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.100 Safari/537.36',
            'accept': '*/*'
        }, params=None)
        return result.status_code

    for link in site['links']:
        lib.log.info(f"Парсим {site['name']}...")
        if check_site(link) != 200:
            lib.log.error(f"Не удалось подключиться! Код ошибки: {check_site(link)}")
            return 0
        parsers[site['parser']](link)
        lib.log.info("Обработка ссылки завершена.")


if __name__ == '__main__':
    pass