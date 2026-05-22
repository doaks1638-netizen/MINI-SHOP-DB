# тут чисто работает с sql запросами
from psycopg import Connection

class BaseRepository:

    @staticmethod
    def _base_except_write(conn:Connection, query: str, params: tuple) -> bool:
        flag = False
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                flag = True
        except Exception as e:
            flag = False
        return flag
    
    @staticmethod
    def _base_get_all(conn:Connection, query):
        with conn.cursor() as cursor:
            cursor.execute(query)
            rez = cursor.fetchall()
        return rez
    
    @staticmethod
    def _base_get_by_id(conn:Connection, query, id):
        with conn.cursor() as cursor:
            cursor.execute(query, (id,))
            rez = cursor.fetchone()
        return rez
    

class UserRepository:
    '''Чистые SQL запросы к users table'''

    @staticmethod
    def get_all(conn:Connection):
        return BaseRepository._base_get_all(conn, 'select id, name, balance from users')
     
    @staticmethod
    def get_by_id(conn:Connection, id:int):
        return BaseRepository._base_get_by_id(conn, 'select id, name, balance from users where id = %s', id)
    
    @staticmethod
    def add_new(conn:Connection, name:str):
        return BaseRepository._base_except_write(conn, 'insert into users (name) values (%s)', (name,))

    @staticmethod
    def delete_user(conn:Connection, id:int):
        return BaseRepository._base_except_write(conn, 'delete from users where id = %s', (id,))


class ProductRepository:
    '''Чистые SQL запросы к products & categories'''

    @staticmethod 
    def get_all_products(conn:Connection):
        return BaseRepository._base_get_all(
            conn,
            'select id, category_id, name, title, price, now_amount from products'
        )
    
    @staticmethod
    def get_by_id(conn:Connection, id:int):
        return BaseRepository._base_get_by_id(
            conn,
            'select id, category_id, name, title, price, now_amount from products where id = %s',
            id
        )

    @staticmethod
    def add_new(conn:Connection, category_id, name, title, now_amount):
        return BaseRepository._base_except_write(
            conn,
            'insert into products (category_id, name, title, now_amount) values (%s, %s, %s, %s)',
            (category_id, name, title, now_amount)
        )
    
    @staticmethod
    def delete_product(conn:Connection, id):
        return BaseRepository._base_except_write(
            conn,
            'delete from products where id = %s',
            (id,)
        )
    
    @staticmethod
    def update_amount(conn:Connection, id, new_amount):
        return BaseRepository._base_except_write(
            conn,
            'update products set now_amount = now_amount + %s where id = %s',
            (new_amount, id)
        )

    @staticmethod
    def update_price(conn:Connection, id, new_price): 
        return BaseRepository._base_except_write(
            conn,
            'update products set price = price + %s where id = %s',
            (new_price, id)
        )


class OrderRepository:
    '''Чистые SQL запросы для работы с orders (orders & order_items tables)'''

    @staticmethod
    def get_all_orders(conn:Connection):
        return BaseRepository._base_get_all(
            conn,
            'select id, user_id, created_at, status from orders'
        )

    @staticmethod
    def get_by_user_id(conn:Connection, id:int):
        return BaseRepository._base_get_by_id(
            conn,
            'select id, user_id, created_at, status from orders where user_id = %s',
            id
        )

    @staticmethod
    def get_order_check(conn:Connection, order_id:int):
        return BaseRepository._base_get_by_id(
            conn,
            'select order_id, product_id, amount, first_price from order_items where order_id = %s',
            order_id
        )
    
    @staticmethod
    def create_order(conn:Connection, user_id, **fields):
        data = {'user_id': user_id}
        if (rez := fields.get('created_at')) is not None:
            data['created_at'] = rez
        if (rez := fields.get('status')) is not None:
            data['status'] = rez
        cols = ', '.join(list(data))
        values = list(data.values())
        placeholders = ', '.join(['%s'] * len(values))

        query = f'insert into orders ({cols}) values ({placeholders}) returning user_id'

        with conn.cursor() as cursor: 
            cursor.execute(query, values)
            rez = cursor.fetchone().user_id

        return rez
        
    @staticmethod
    def add_order_products(conn:Connection, order_id:int, product_id:int, amount, first_price:int):
        return BaseRepository._base_except_write(
            conn,
            'insert into order_items (order_id, product_id, amount, first_price) values (%s, %s, %s, %s)',
            (order_id, product_id, amount, first_price)
        )
    
class CategoriesRepository:

    @staticmethod
    def create_repository(conn:Connection, name):
        return BaseRepository._base_except_write(conn, 'insert into categories (name) values (%s)', (name,))
    
    @staticmethod
    def get_all_repository(conn:Connection, name):
        return BaseRepository._base_get_all(conn, 'select id, name from categories')
    
    