import psycopg2
import psycopg2.extras
from singleton_decorator import singleton
# my libs
from read_config import read_parameters, read_json


@singleton
class Database(object):
    _cur: psycopg2

    def __init__(self):
        self._db_parameters = read_parameters('postgresql')
        self.__db_connection = psycopg2.connect(**self._db_parameters)
        self.__db_connection.autocommit = True
        self._cur = self.__db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.perform_checks()

    def connect(self):

        self.__db_connection = psycopg2.connect(**self._db_parameters)
        self.__db_connection.autocommit = True



    def perform_checks(self):
        def schemas_create():
            # self.connect()
            sql1 = f"""CREATE SCHEMA IF NOT EXISTS notifications AUTHORIZATION postgres;"""
            self._cur.execute(sql1)
            sql2 = f"""CREATE SCHEMA IF NOT EXISTS sites AUTHORIZATION postgres;"""
            self._cur.execute(sql2)
            sql3 = f"""CREATE SCHEMA IF NOT EXISTS telegram AUTHORIZATION postgres;"""
            self._cur.execute(sql3)

        def site_table_create(name):
            # self.connect()
            sql = f"""CREATE TABLE if not exists sites.{name} (
                    id int4 GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY ,
                    link text NOT NULL UNIQUE ,
                    price int4 NULL,
                    price_history json NULL,
                    available float4 NULL,
                    "name" text NOT NULL UNIQUE,
                    main_id int4 NULL);"""
            self._cur.execute(sql)

        def notifications_table_create(name) -> None:
            # self.connect()
            sql = f"""CREATE TABLE if not exists notifications.{name} 
            (
            id int4 GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY ,
            time float4 ,
            type text ,
            content text ,
            processed bool DEFAULT FALSE
            );"""
            self._cur.execute(sql)

        def telegram_users_table_create() -> None:
            # self.connect()
            sql = f"""CREATE TABLE if not exists telegram.user_list
                            (user_id int4 PRIMARY KEY UNIQUE);"""
            self._cur.execute(sql)

        # Создание основных таблиц при старте
        schemas_create()
        telegram_users_table_create()
        notifications_table_create("main_stack")

        # Создание таблицы под каждый обрабатываемый сайт
        for table_name in read_json().keys():
            site_table_create(table_name)
            notifications_table_create(table_name)

        # Проверка наличия пользовательских таблиц, для целостности
        tg_users_list = self.query(f"""SELECT user_id FROM telegram.user_list;""")
        if tg_users_list:
            tg_table_list = self.query(f"""SELECT table_name
                                      FROM information_schema.tables
                                     WHERE table_schema='telegram'
                                       AND table_type='BASE TABLE';""")
            for user in tg_users_list:
                if not any(str(user['user_id']) in s['table_name'] for s in tg_table_list):
                    self.create_user_table(user['user_id'])

    def query(self, statement: str, args: tuple = None):
        # self.connect()
        if args:
            self._cur.execute(statement, args)
        else:
            self._cur.execute(statement)
        # print("=============================================")
        # pprint(getmembers(self._cur))
        if self._cur.description is None:
            return None
        else:
            result = []
            fetch = self._cur.fetchone()
            while fetch:
                result.append(fetch)
                fetch = self._cur.fetchone()
            return result

    def create_user_table(self, user_id):
        # self.connect()
        sql = f"""CREATE TABLE IF NOT EXISTS telegram.id_{user_id} 
            (id int4 GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY ,  
            time float4 ,
            content text , 
            sent bool DEFAULT FALSE);"""
        self._cur.execute(sql)


if __name__ == '__main__':
    db = Database()
