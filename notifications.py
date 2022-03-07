from datetime import datetime
# my libs
import bot_control
from lib import DB, log


def add_new_notification(site, notification_type, content):
    _db = DB
    sql = f"""INSERT INTO notifications.{site} (time, type, content)
                        VALUES (%s, %s, %s);"""
    args = (datetime.now().timestamp(), notification_type, content)
    _db.query(sql, args)
    

def add_new_telegram_user(user_id):
    _db = DB
    sql = f"""INSERT INTO telegram.user_list (user_id) VALUES (%s) ON CONFLICT DO NOTHING """
    _db.query(sql, (user_id,))
    _db.create_user_table(user_id)


def process_notifications(site):
    """Обрабатывает уведомления из таблицы конкретного сайта, и сохраняет сообщение в таблицу main_stack."""
    _db = DB
    log.info(f"Ищем новые уведомления с сайта {site}...")
    sql_get_notifications = f"SELECT * FROM notifications.{site} WHERE processed = false"
    result = _db.query(sql_get_notifications)

    if len(result) > 25:
        repeat_process = True
        result = result[:25]
    else:
        repeat_process = False

    if not result:
        log.info(f"Нет новых уведомлений.")
        return
    else:
        log.info(f"Новых уведомлений: {len(result)}.")

    # Собираем уведомления в словарь с разделами по типу уведомлений
    notifications_dict = {}
    for notification in result:
        if notification["type"] not in notifications_dict.keys():
            notifications_dict[notification["type"]] = []
        notifications_dict[notification["type"]].append(notification["content"])

    # Формируем уведомление
    message = f"Изменения на сайте <b>{site}</b>:\n============================================\n"

    for section in notifications_dict:
        message += f"<b>{section}</b>\n"
        for entry in sorted(notifications_dict[section]):
            message += f"{entry}\n"
        message += f"\n"

    # сохраняем уведомление в main_stack
    sql_save_message = f"""INSERT INTO notifications.main_stack (time, content) VALUES (%s, %s);"""
    _db.query(sql_save_message, (datetime.now().timestamp(), message))

    # отмечаем уведомления из таблицы site как обработанные
    for notification in result:
        sql_update_processed = f"UPDATE notifications.{site} SET processed = true WHERE id = {notification['id']}"
        _db.query(sql_update_processed)

    if repeat_process:
        process_notifications(site)


def prepare_notifications_for_users():
    """Раскидывает уведомления из main_stack в личные таблицы пользователей."""
    _db = DB
    sql = f"SELECT * FROM notifications.main_stack WHERE processed = false"
    new_messages = _db.query(sql)
    if not new_messages:
        return
    get_user_list = f"SELECT user_id FROM telegram.user_list"
    user_list = list("id_" + str(record['user_id']) for record in _db.query(get_user_list))
    for user in user_list:
        for message in new_messages:
            sql_q = f"INSERT INTO telegram.{user} (time, content) VALUES (%s, %s);"
            _db.query(sql_q, (datetime.now().timestamp(), message['content']))
            sql_update = f"UPDATE notifications.main_stack SET processed = true WHERE id = {message['id']}"
            _db.query(sql_update)


def send_updates_to_users(particular_user=None):
    def send_to_user(user_id):
        user_table = 'id_' + str(user_id)
        get_notifications = f"SELECT * FROM telegram.{user_table} WHERE sent = false"
        new_notifications = _db.query(get_notifications)
        for ntf in new_notifications:
            if not bot_control.send_message(user_id, ntf['content']):
                raise ConnectionError
            else:
                update_viewed = f"UPDATE telegram.{user_table} SET sent = true WHERE id = {ntf['id']}"
                _db.query(update_viewed)

    _db = DB
    get_user_list = f"SELECT user_id FROM telegram.user_list"
    user_list = list(str(s['user_id']) for s in _db.query(get_user_list))
    if not particular_user:
        for user in user_list:
            send_to_user(user)
    else:
        send_to_user(particular_user)
