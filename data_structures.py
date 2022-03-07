from dataclasses import dataclass
from datetime import datetime
import json
# my libs
from lib import DB
import notifications


@dataclass()
class Item:
    """Класс базового товара. Скорее абстракция, на самом деле."""
    _name: str = None
    _id: int = None
    _inactive: int = 0


class ParsedItem(Item):
    _DB = DB
    _price: int
    _availability: float
    _site: str
    _link: str
    _price_history: json

    def __init__(self, site, name, link, price):
        self._site = site
        self._name = name
        self._link = link
        self._price = price
        # _price_history - JSON-словарь с датами изменения цены.
        self._price_history = json.dumps({int(datetime.now().timestamp()): price}, indent=4)
        # _availability - когда товар был замечен в последний раз
        self._availability = int(datetime.now().timestamp())

    def check_link_existence_in_source_table(self):
        """Проверяет, существует ли данный элемент в базе товаров с обрабатываемого сайта.
        При успехе возвращает True и устанавливает значение _id."""
        # смотрим в site
        sql = f"SELECT * FROM sites.{self._site} WHERE link = '{self._link}' OR name = '{self._name}'"
        result = self._DB.query(sql)
        if result:
            self._id = result[0]['id']
            return True
        else:
            return False

    def save_new_item(self):
        """Добавляет новый элемент в суб-таблицу."""
        sql_sub = f"""INSERT INTO sites.{self._site} (name, link, price, price_history, available)
                    VALUES (%s, %s, %s, %s, %s)"""
        args_sub = (self._name, self._link, self._price, self._price_history, self._availability)
        self._DB.query(sql_sub, args_sub)
        # сохраняем уведомление
        message = f"<a href='{self._link}'>{self._name}</a> <b>{self._price}</b>р."
        notifications.add_new_notification(self._site, "Новый товар:", message)

    def update_item(self):
        """Обновляет информацию в БД."""

        def update_price_history(price_arr: json or dict, append: json):  # Вставляет новую цену в начало истории цен
            def json_keys_to_int(x):
                if isinstance(x, dict):
                    return {int(k): v for k, v in x.items()}
                return x

            def list_to_dict(lst):
                dct = {}
                for i in lst:
                    dct[i[0]] = i[1]
                return dct

            if type(price_arr) == dict:
                history = price_arr
            elif type(price_arr) == list:
                history = list_to_dict(price_arr)
            else:
                history = json.loads(price_arr, object_hook=json_keys_to_int)

            new_price = json.loads(append, object_hook=json_keys_to_int)
            history.update(new_price)
            history = json_keys_to_int(history)
            return json.dumps(sorted(history.items(), reverse=True), indent=4)

        # Проверяем, есть ли id - на всякий случай.
        if not self._id:
            return None

        # Вытаскиваем из базы словарь с данными о товаре
        sql_fetch = f"""SELECT * FROM sites.{self._site} WHERE id = {self._id}"""
        record = self._DB.query(sql_fetch)[0]

        # Вычисляем, как давно товар был замечен в последний раз.
        time_from_last_appearance = datetime.fromtimestamp(self._availability) - datetime.fromtimestamp(record['available'])
        # Если товара не было более 3 дней - уведомляем
        if time_from_last_appearance.total_seconds() > 259200:
            # сохраняем уведомление
            message = f"<a href='{self._link}'>{self._name}</a>, пропал {time_from_last_appearance.days} {'дня' if time_from_last_appearance.days <= 4 else 'дней'} назад."
            notifications.add_new_notification(self._site, "Вернулись на сайт:", message)

        # если цена не изменилась, записываем временную метку о доступности
        if record['price'] == self._price:
            sql = f"""UPDATE sites.{self._site} 
                              SET available = {self._availability} 
                              WHERE id = {self._id}"""
        else:
            # если цена изменилась - добавляем новую запись в историю цен
            self._price_history = update_price_history(record['price_history'], self._price_history)
            # сохраняем уведомление
            message = f"<a href='{self._link}'>{self._name}</a> {record['price']}р. -> <b>{self._price}</b>р."
            notifications.add_new_notification(self._site, "Изменилась цена:", message)
            # обновляем price, price_history и available
            sql = f"""UPDATE sites.{self._site} 
                      SET price = {self._price}, price_history = '{self._price_history}', available = {self._availability} 
                      WHERE id = {self._id}"""
        self._DB.query(sql)
