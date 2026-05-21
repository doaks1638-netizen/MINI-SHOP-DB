# конфиг для импорта переменных окружения

import os
from dotenv import load_dotenv

load_dotenv()

class Db_config:
    
    def __init__(self):
        self.host = os.getenv('HOST')
        self.port = os.getenv('PORT')
        self.dbname = os.getenv('DBNAME')
        self.user = os.getenv('USER')
        self.password = os.getenv('PASSWORD')
        self._log_show = False

    def get_for_connect(self):
        if not self._log_show:
            print("--- ЛОГ СИСТЕМНОЙ КОНФИГУРАЦИИ ---")
            print(f"БД Хост:      {self.host}")
            print(f"БД Порт:      {self.port}")
            print(f"БД Имя:       {self.dbname}")
            print(f"Пользователь: {self.user}")
            print(f"Пароль: {self.password}")
            self._log_show = True
        return {'host':self.host, 'port':self.port, 
                'dbname':self.dbname,'user':self.user,
                'password':self.password}

DB = Db_config()