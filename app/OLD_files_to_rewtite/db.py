# настройка подключения
import psycopg
from psycopg.rows import namedtuple_row
from config import DB

def get_connect():
    return psycopg.connect(**DB.get_for_connect(), row_factory=namedtuple_row)