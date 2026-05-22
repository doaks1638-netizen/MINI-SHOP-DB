# вся логика приложения (тут все транзакции и проверки) БЕЗ sql!
# прописать подключение через namedtuple
from repositories import UserRepository, ProductRepository, OrderRepository, CategoriesRepository
from db import get_connect

# юзеры

def show_all_users():
    with get_connect() as conn:
        rez = UserRepository.get_all(conn)
    return rez

def show_by_id_users(id):
    with get_connect() as conn:
        rez = UserRepository.get_by_id(conn, id)
    return rez

def add_user(name):
    with get_connect() as conn:
        rez = UserRepository.add_new(conn, name)
        if not rez:
            raise ValueError('Ошибка при добвление пользователя! Введите верное имя')

def delete_user(id):
    with get_connect() as conn:
        rez = UserRepository.delete_user(conn, id)
        if not rez:
            raise ValueError('Ошибка при удалении юзера! Введите нормальный id!')
    
# товары

def get_all_products():
    with get_connect() as conn:
        rez = ProductRepository.get_all_products(conn)
    return rez

def get_id_products(id):
    with get_connect() as conn:
        rez = ProductRepository.get_by_id(conn, id)
    return rez

def add_new_product(category_id, name, title, now_amount):
    with get_connect() as conn:
        rez = ProductRepository.add_new(conn, category_id, name, title, now_amount)
        if not rez:
            raise ValueError('Ошибки при добавление пользователя! ' \
            'Пожалуйства проверьте правильность данных')
        
def delete_product(id):
    with get_connect() as conn:
        rez = ProductRepository.delete_product(conn,id)
        if not rez:
            raise ValueError('Не удалось удалось удалить пользователя!')
        
def update_product_price(id, new_price):
    with get_connect() as conn:
        rez = ProductRepository.update_price(conn, id, new_price)
        if not rez:
            raise ValueError('Обновление цены не произошло! Проверите id или корекность цены (>0)')

def update_product_amount(id, new_am):
    with get_connect() as conn:
        rez = ProductRepository.update_price(conn, id, new_am)
        if not rez:
            raise ValueError('Обновление цены не произошло! Проверите id или корекность количетства (>0)')

# категории

def create_category(name):
    with get_connect() as conn:
        rez = CategoriesRepository.create_repository(conn, name)
        if not rez:
            raise ValueError('Ошибка при создании категории! Проверить корекность имени!')
        
def get_all_categories():
    with get_connect() as conn:
        rez = CategoriesRepository.get_all_repository(conn)
    return  rez

# заказы 


    