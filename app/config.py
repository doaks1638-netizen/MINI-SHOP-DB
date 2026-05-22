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
        
    def get_for_connect(self):
        return {'host':self.host, 'port':self.port, 
                'dbname':self.dbname,'user':self.user,
                'password':self.password}


DB = Db_config()