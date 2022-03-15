import threading
import time
import sys
import requests
# my libs
import notifications
import parser_classes
import lib
import bot_control
from read_config import read_json, read_parameters


def parse_site(site: dict):
    try:
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

    except Exception as e:
        lib.log.exception("ОЙ!:")
        lib.exception_count += 1
        bot_control.send_message(read_parameters('telegram')['my_tg_id'], f"Ошибка при парсинге:\n{e}\n{link}\n")
        if lib.exception_count >= 3:
            lib.log.critical("Слишком много ошибок, отменяем задачу.")
            bot_control.send_message(read_parameters('telegram')['my_tg_id'], f"НАСЯЛЬНИКЕ ПЕСДЕC")
            sys.exit()
        time.sleep(10)
        parse_site(site)


def send_notifications(particular_user=None, site_list=read_json().keys()):
    lib.exception_count = 0
    for table in site_list:
        notifications.process_notifications(table)
    notifications.prepare_notifications_for_users()
    lib.log.info(f"Отправляем уведомления пользователям...")
    try:
        notifications.send_updates_to_users(particular_user)
        lib.log.info(f"Отправили.")
    except Exception as e:
        lib.log.exception("ОЙ!:")
        lib.exception_count += 1
        time.sleep(5)
        bot_control.send_message(read_parameters('telegram')['my_tg_id'], f"Ошибка при отправке сообщения:\n{e}\n")
        if lib.exception_count >= 3:
            lib.log.critical("Слишком много ошибок, завершаем работу.")
            bot_control.send_message(read_parameters('telegram')['my_tg_id'], f"НАСЯЛЬНИКЕ ПЕСДЕC")
            sys.exit()
        time.sleep(5)
        notifications.send_updates_to_users(particular_user)


if __name__ == '__main__':
    sites = read_json()
    parse_site(sites['ttt'])
    parse_site(sites['mobitech'])
    parse_site(sites['foks'])
    parse_site(sites['donbass_smart'])
    send_notifications()
    lib.log.info("Отработали, новый запуск через 30 минут.")
