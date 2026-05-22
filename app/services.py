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
    try:
        with get_connect() as conn:
            UserRepository.add_new(conn, name)
    except Exception:
        raise ValueError('Ошибка при добвление пользователя! Введите верное имя')

def delete_user(id):
    try:
        with get_connect() as conn:
            UserRepository.delete_user(conn, id)
    except Exception:
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
    try:
        with get_connect() as conn:
            ProductRepository.add_new(conn, category_id, name, title, now_amount)
    except Exception:
        raise ValueError('Ошибки при добавление пользователя! ' \
            'Пожалуйства проверьте правильность данных')
        
def delete_product(id):
    try:
        with get_connect() as conn:
            ProductRepository.delete_product(conn, id)
    except Exception:
        raise ValueError('Не удалось удалось удалить пользователя!')
        
def update_product_price(id, new_price):
    try:
        with get_connect() as conn:
            ProductRepository.update_price(conn, id, new_price)
    except Exception:
        raise ValueError('Обновление цены не произошло! Проверите id или корекность цены (>0)')

def update_product_amount(id, new_am):
    try:
        with get_connect() as conn:
            ProductRepository.update_price(conn, id, new_am)
    except Exception:
        raise ValueError('Обновление цены не произошло! Проверите id или корекность количетства (>0)')

# категории

def create_category(name):
    try:
        with get_connect() as conn:
            CategoriesRepository.create_repository(conn, name)
    except Exception:
        raise ValueError('Ошибка при создании категории! Проверить корекность имени!')
        
def get_all_categories():
    with get_connect() as conn:
        rez = CategoriesRepository.get_all_repository(conn)
    return rez

# заказы 
'''
- создание заказа и наполнение его (при нажатии купить сейчас) - done
- создание заказа и выполнение его (при выборке из корзины) + автоматическое удаление из корзины
- попопление корзины ipsert
- просмотр всех заказов
- просмотр активвных заказов / доставленных
- поменять статус заказа
- при добавлении товара списать его количество и проверить баланс пользователя
'''


def buy_product_now(user_id, product_id, amount, order_id = None):
    try:
        with get_connect() as conn:
            price_now = ProductRepository.get_by_id(conn, product_id).price 
            user_balance = UserRepository.get_by_id(conn, user_id).balance
            product_amount = ProductRepository.get_by_id(conn, product_id).now_amount

            if product_amount < amount:
                raise ValueError(f'Недостаточно денег на балансе! Всего осталось {product_amount}')
            if user_balance < product_amount:
                raise ValueError('Недостаточно денег на балансе!')
            
            order_id = (OrderRepository.create_order(conn, user_id).id if order_id is None else order_id)
            OrderRepository.add_order_products(conn, order_id, product_id, amount, price_now)
    except Exception:
        raise ValueError('Некоректный айди товара!')
    
def create_full_order(user_id, products:dict):
    '''Получает user_id и словарем (айди:количество), удаляет из коризны и оформляет заказ'''
    try:
        with get_connect() as conn:
            order_id = OrderRepository.create_order(conn, user_id).id 
            for id, amount in products.items():
                buy_product_now(user_id, id, amount, order_id=order_id)
    except Exception:
        raise ValueError('При попытке оформления заказа возникла ошибка! Повторите позже')
    

