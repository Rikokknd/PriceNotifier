import threading
import time
import sys
# my libs
import notifications
import run_parser
from lib import lock, log
import lib
import bot_control
from read_config import read_json, read_parameters


def send_notifications(particular_user=None, site_list=read_json().keys()):
    while True:
        with lock:
            for table in site_list:
                notifications.process_notifications(table)
            notifications.prepare_notifications_for_users()
            lib.log.info(f"Отправляем уведомления пользователям...")
            try:
                notifications.send_updates_to_users(particular_user)
            except Exception as e:
                log.exception("ОЙ!:")
                lib.exception_count += 1
                time.sleep(5)
                bot_control.send_message(read_parameters('telegram')['my_tg_id'], f"Ошибка при отправке сообщения:\n{e}\n")
            finally:
                if lib.exception_count >= 25:
                    log.critical("Слишком много ошибок, завершаем работу.")
                    bot_control.send_message(read_parameters('telegram')['my_tg_id'], f"НАСЯЛЬНИКЕ ПЕСДЕC")
                    sys.exit()
                time.sleep(5)
                notifications.send_updates_to_users(particular_user)

            lib.log.info(f"Отправили.")
        # TODO: настроить адекватное время рассылки уведомлений
        time.sleep(1800)


def parsing_thread(site: dict):
    try:
        while True:
            with lock:
                run_parser.parse(site)
                log.info("Отработали, новый запуск через 30 минут.")

            time.sleep(1800)

    except Exception as e:
        log.exception("ОЙ!:")
        lib.exception_count += 1
        bot_control.send_message(read_parameters('telegram')['my_tg_id'], f"Ошибка при парсинге:\n{e}\n")

    finally:
        if lib.exception_count >= 25:
            log.critical("Слишком много ошибок, завершаем работу.")
            bot_control.send_message(read_parameters('telegram')['my_tg_id'], f"НАСЯЛЬНИКЕ ПЕСДЕC")
            sys.exit()
        time.sleep(10)
        parsing_thread(site)


if __name__ == '__main__':
    sites = read_json()
    thread1 = threading.Thread(target=parsing_thread, args=(sites['ttt'],))
    thread2 = threading.Thread(target=parsing_thread, args=(sites['mobitech'],))
    thread3 = threading.Thread(target=parsing_thread, args=(sites['foks'],))
    thread4 = threading.Thread(target=parsing_thread, args=(sites['donbass_smart'],))
    thread9 = threading.Thread(target=send_notifications)
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread9.start()
