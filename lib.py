# external libs
import logging
from threading import Lock
from datetime import datetime
import telegram
from singleton_decorator import singleton
from telegram.utils import request
import sys

# my libs
from postgre import Database
from read_config import read_parameters


@singleton
class MyBot(telegram.Bot):
    def __init__(self):
        super().__init__(token=read_parameters('telegram')['token'], request=request.Request(con_pool_size=8))


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename=f'logs/{datetime.now().strftime("%m_%d_%Y")}.log',
                    filemode='a')
log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


lock = Lock()
DB = Database()
bot = MyBot()

notifications_pending = 0
last_update = 0
exception_count = 0