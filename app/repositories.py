# тут чисто работает с sql запросами
from psycopg import Connection

class UserRepository:
    '''Чистые SQL запросы к users table'''

    @staticmethod
    def get_all(conn:Connection):
        with conn.cursor() as cursor:
            cursor.execute('select id, name, ' \
            'balance from users')
            rez = cursor.fetchall()
        return rez
    
    @staticmethod
    def get_by_id(conn:Connection, id:int):
        with conn.cursor() as cursor:
            cursor.execute('select id, name, ' \
            'balance from users where id = %s', (id, ))
            rez = cursor.fetchall()
        return rez
    
    @staticmethod
    def add_new(conn:Connection, name:str):
        flag = False
        try:
            with conn.cursor() as cursor:
                cursor.execute('insert into users (name) values (%s)', (name,))
                flag = True
        except Exception as e:
            flag = False
        return flag


class ProductRepository:
    '''Чистые SQL запросы к products & categories'''

    @staticmethod 
    def get_all_products(conn:Connection, category_info=False):
        with conn.cursor() as cursor:
            if not category_info:
                cursor.execute('select ' \
                'id, category_id,' \
                'name, title,' \
                'price, now_amount ' \
                'from products')
            else:
                cursor.execute('select ' \
                'p.id product_id, p.category_id,' \
                'p.name product_name, p.title,' \
                'p.price, p.now_amount, ' \
                'c.id category_id, c.name category_name ' \
                'from products p join categories c on p.category_id = c.id')
            rez = cursor.fetchall()
        return rez
    
    @staticmethod
    def get_by_id(conn:Connection, id:int ,category_info=False):
        with conn.cursor() as cursor:
            if not category_info:
                cursor.execute('select ' \
                'id, category_id,' \
                'name, title,' \
                'price, now_amount ' \
                'from products' \
                ' where id = %s', (id,))
            else:
                cursor.execute('select ' \
                'p.id product_id, p.category_id,' \
                'p.name product_name, p.title,' \
                'p.price, p.now_amount, ' \
                'c.id category_id, c.name category_name ' \
                'from products p join categories c on p.category_id = c.id ' \
                'where p.id = %s', (id,))
            rez = cursor.fetchall()
        return rez

    @staticmethod
    def add_new(conn:Connection, category_id, name, title, now_amount):
        flag = False
        try:
            with conn.cursor() as cursor:
                cursor.execute('insert into products (category_id, name, title, now_amount) values (%s, %s, %s, %s)', (category_id, name, title, now_amount))
                flag = True
        except Exception as e:
            flag = False
        return flag
    
    @staticmethod
    def update_amount(conn:Connection, id, new_amount):
        flag = False
        try:
            with conn.cursor() as cursor:
                cursor.execute('update products set now_amount = now_amount + %s where id = %s', (new_amount, id))
                flag = True
        except Exception as e:
            flag = False
        return flag

    @staticmethod
    def update_price(conn:Connection, id, new_price): 
        flag = False
        try:
            with conn.cursor() as cursor:
                cursor.execute('update products set price = price + %s where id = %s', (new_price, id))
                flag = True
        except Exception as e:
            flag = False
        return flag 

class OrderRepository:
    '''Чистые SQL запросы для работы с orders (orders & order_items tables)'''

    @staticmethod
    def get_all_orders(conn:Connection):
        with conn.cursor() as cursor:
            cursor.execute('select id, user_id, created_at, '
            'status from orders')
            rez = cursor.fetchall()
        return rez

    @staticmethod
    def get_by_user_id(conn:Connection, id:int):
        with conn.cursor() as cursor:
            cursor.execute('select id, user_id, created_at, '
            'status from orders'
            ' where user_id = %s', (id,))
            rez = cursor.fetchall()
        return rez

    @staticmethod
    def get_order_check(conn:Connection, order_id:int):
        with conn.cursor() as cursor:
            cursor.execute('select order_id, ' \
            'product_id, amount, first_price from order_items ' \
            'where order_id = %s', (order_id,))
            rez = cursor.fetchall()
        return rez
    
    @staticmethod
    def create_order(conn:Connection,user_id,**fields):
        data = {'user_id':user_id}
        if (rez := fields.get('created_at')) is not None:
            data['created_at'] = rez
        if (rez := fields.get('status')) is not None:
            data['status'] = rez
        fields = ', '.join(list(data))
        values = list(data.values())
        placeholders = ', '.join(['%s'] * len(values))

        query = f'''
        insert into orders ({fields}) values ({placeholders}) returning user_id
        '''

        with conn.cursor() as cursor: 
            cursor.execute(query, values)
            rez = cursor.fetchone().user_id

        return rez
        
    @staticmethod
    def add_order_products(conn:Connection, order_id:int, product_id:int, amount, first_price:int):
        flag = False
        try:
            with conn.cursor() as cursor: 
                cursor.execute('insert into order_items (order_id, product_id, amount, first_price) ' \
                'values (%s, %s, %s, %s)', (order_id, product_id, amount, first_price))
                flag = True
        except Exception:
            flag = False
        return flag
