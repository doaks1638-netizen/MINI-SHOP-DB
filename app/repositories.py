# тут чисто работает с sql запросами
from psycopg import Connection

class BaseRepository:

    @staticmethod
    def _base_query(conn:Connection, query: str, params: tuple) -> bool:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
    
    @staticmethod
    def _base_get_all(conn:Connection, query):
        with conn.cursor() as cursor:
            cursor.execute(query)
            rez = cursor.fetchall()
        return rez
    
    @staticmethod
    def _base_get_by_id(conn:Connection, query, id, for_update = False, update_query = None):
        with conn.cursor() as cursor:
            if not for_update:
                cursor.execute(query, (id,))
                rez = cursor.fetchone()
            else:
                if update_query is not None:
                    cursor.execute(update_query, (id,))
                    rez = cursor.fetchone()  
        return rez
    
    @staticmethod
    def _base_get_by_id_all(conn:Connection, query, id):
        with conn.cursor() as cursor:
            cursor.execute(query, (id,))
            rez = cursor.fetchall()
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
        BaseRepository._base_query(conn, 'insert into users (name) values (%s)', (name,))

    @staticmethod
    def delete_user(conn:Connection, id:int):
        BaseRepository._base_query(conn, 'delete from users where id = %s', (id,))


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
        BaseRepository._base_query(
            conn,
            'insert into products (category_id, name, title, now_amount) values (%s, %s, %s, %s)',
            (category_id, name, title, now_amount)
        )
    
    @staticmethod
    def delete_product(conn:Connection, id):
        BaseRepository._base_query(
            conn,
            'delete from products where id = %s',
            (id,)
        )
    
    @staticmethod
    def update_amount(conn:Connection, id, new_amount):
        BaseRepository._base_query(
            conn,
            'update products set now_amount = now_amount + %s where id = %s',
            (new_amount, id)
        )

    @staticmethod
    def update_price(conn:Connection, id, new_price): 
        BaseRepository._base_query(
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
        return BaseRepository._base_get_by_id_all(
            conn,
            'select id, user_id, created_at, status from orders where user_id = %s',
            id
        )

    @staticmethod
    def get_order_check(conn:Connection, order_id:int):
        return BaseRepository._base_get_by_id_all(
            conn,
            'select order_id, product_id, amount, first_price from order_items where order_id = %s',
            order_id
        )
    
    @staticmethod
    def get_active_orders(conn:Connection, user_id):
        return BaseRepository._base_get_by_id_all(
            conn,
            '''
            select id, user_id, created_at, status from orders where user_id = %s and status in ('prepared', 'finish', 'delivery')
            ''',
            user_id
        )
    
    @staticmethod
    def delivered_orders(conn:Connection, user_id):
        return BaseRepository._base_get_by_id_all(
            conn,
            '''
            select id, user_id, created_at, status from orders where user_id = %s and status = 'delivered'
            ''',
            user_id
        )
    
    @staticmethod
    def create_order(conn:Connection, user_id):
        BaseRepository._base_query(conn, 'insert into orders (user_id) values (%s) returning id', (user_id,))
    
    @staticmethod
    def change_order_status(conn:Connection, order_id, status):
        BaseRepository._base_query(conn, 'update orders set status = %s where id = %s', (status, order_id))
        
    @staticmethod
    def add_order_products(conn:Connection, order_id:int, product_id:int, amount, first_price:int):
        BaseRepository._base_query(
            conn,
            'insert into order_items (order_id, product_id, amount, first_price) values (%s, %s, %s, %s)',
            (order_id, product_id, amount, first_price)
        )
    
class CategoriesRepository:

    @staticmethod
    def create_repository(conn:Connection, name):
        BaseRepository._base_query(conn, 'insert into categories (name) values (%s)', (name,))
    
    @staticmethod
    def get_all_repository(conn:Connection, name):
        BaseRepository._base_get_all(conn, 'select id, name from categories')

class CartRepository:

    @staticmethod
    def bucket_init(conn:Connection, user_id):
        BaseRepository._base_query(conn, 'insert into cart (user_id) values (%s)', (user_id,))
    
    