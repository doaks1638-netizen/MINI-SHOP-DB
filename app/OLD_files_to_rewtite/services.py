# вся логика приложения (тут все транзакции и проверки) БЕЗ sql!
# прописать подключение через namedtuple
from repositories import UserRepository, ProductRepository, OrderRepository, CategoriesRepository, CartRepository
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
        
def plus_product_price(id, new_price):
    try:
        with get_connect() as conn:
            ProductRepository.plus_price(conn, id, new_price)
    except Exception:
        raise ValueError('Обновление цены не произошло! Проверите id или корекность цены (>0)')

def plus_product_amount(id, new_am):
    try:
        with get_connect() as conn:
            ProductRepository.plus_amount(conn, id, new_am)
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

def buy_product_now(user_id, product_id, amount):
    if amount < 1:
        raise ValueError('Можно купить только больше 1 товара')

    try:
        with get_connect() as conn:

            product = ProductRepository.get_by_id(conn, product_id, for_update=True) 
            if product is None:
                    raise ValueError('Данного товара не существует!')
            
            price_now, product_amount = product.price, product.now_amount
            user = UserRepository.get_by_id(conn, user_id, for_update=True)
            if user is None:
                raise ValueError('Данного пользователя не существует!')

            user_balance = user.balance

            if product_amount < amount:
                raise ValueError(f'Недостаточно товара в магазине! Всего осталось {product_amount}')
            if user_balance < (price_now * amount):
                raise ValueError('Недостаточно денег на балансе!')
            
            order_id = OrderRepository.create_order(conn, user_id).id
            OrderRepository.add_order_products(conn, order_id, product_id, amount, price_now)

            ProductRepository.plus_amount(conn, product_id, -amount)
            UserRepository.plus_balance(conn, user_id, -(price_now*amount))

    except ValueError:
        raise
    except Exception:
        raise ValueError('Произошла ошибка! Повторить позже..')
    
def create_full_order(user_id, products:dict):
    '''Получает user_id и словарем (айди:количество), удаляет из коризны и оформляет заказ'''  
    if not products:
        raise ValueError('Не выбрано не одного заказа!')

    try:
        with get_connect() as conn:
            user = UserRepository.get_by_id(conn, user_id, for_update=True)
            if user is None:
                raise ValueError('Данного пользователя не существует!')
            user_balance = user.balance
            order_id = OrderRepository.create_order(conn, user_id).id

            total_sum = 0

            for product_id, amount in products.items():

                if amount < 1:
                    raise ValueError('Можно купить только больше 1 товара')

                product = ProductRepository.get_by_id(conn, product_id, for_update=True) 
                if product is None:
                    raise ValueError('Данного товара не существует!')
                
                price_now, product_amount = product.price, product.now_amount

                if product_amount < amount:
                    raise ValueError(f'Недостаточно товара в магазине! Всего осталось {product_amount}')
                
                total_sum += (price_now * amount)

                if user_balance < total_sum:
                    raise ValueError('Недостаточно денег на балансе!')

                ProductRepository.plus_amount(conn, product_id, -amount)
                OrderRepository.add_order_products(conn, order_id, product_id, amount, price_now)
                CartRepository.delete_from_cart(conn, user_id, product_id)
             
            UserRepository.plus_balance(conn, user_id, -total_sum)       
                
    except ValueError:
        raise
    except Exception:
        raise ValueError('Произошла ошибка! Повторить позже..')

def show_all_orders():
    with get_connect() as conn:
        rez = OrderRepository.get_all_orders(conn)
    return rez

def show_user_orders(user_id):
    with get_connect() as conn:
        rez = OrderRepository.get_by_user_id(conn, user_id)
    return rez

def show_user_active_orders(user_id):
    with get_connect() as conn:
        rez = OrderRepository.get_active_orders(conn, user_id)
    return rez

def show_user_delivered_orders(user_id):
    with get_connect() as conn:
        rez = OrderRepository.delivered_orders(conn, user_id)
    return rez

def change_order_status(order_id, status):
    if status not in ['created', 'prepared', 'finish', 'delivery', 'delivered']:
        raise ValueError('Некоректное значение статуса')
    try:
        with get_connect() as conn:
            OrderRepository.change_order_status(conn,order_id, status)
    except Exception:
        raise ValueError('Не удалось изменить статус') 
        

# корзина
    
def show_all_cart_id(user_id):
    with get_connect() as conn:
        rez = CartRepository.get_user_cart(conn, user_id)
    return rez
    
def delete_from_cart(user_id, product_id):
    with get_connect() as conn:
        return CartRepository.delete_from_cart(conn, user_id, product_id)
    
def add_to_cart(user_id, product_id, amount):
    if amount < 1:
        raise ValueError('Количество товара должно быть больше 0')

    with get_connect() as conn:
        user = UserRepository.get_by_id(conn, user_id)
        if user is None:
            raise ValueError('Данного пользователя не существует!')

        product = ProductRepository.get_by_id(conn, product_id)
        if product is None:
            raise ValueError('Данного товара не существует!')

        return CartRepository.add_to_cart(conn, user_id, product_id, amount)