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
            ProductRepository.update_amount(conn, id, new_am)
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
- обновить статус заказа
'''


def buy_product_now(user_id, product_id, amount):
    if amount < 1:
        raise ValueError('Можно купить только больше 1 товара')

    try:
        with get_connect() as conn:

            product = ProductRepository.get_by_id(conn, product_id, for_update=True) 
            if product is None:
                    raise ValueError('Данного товара не существует!')
            
            price_now, product_amount = product.price, product.now_amount
            user_balance = UserRepository.get_by_id(conn, user_id, for_update=True).balance

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
            user_balance = UserRepository.get_by_id(conn, user_id, for_update=True).balance
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
             
            UserRepository.plus_balance(conn, user_id, -total_sum)       
                
    except ValueError:
        raise
    except Exception:
        raise ValueError('Произошла ошибка! Повторить позже..')

