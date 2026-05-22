# cхема для развертывания бд

drop schema public cascade;
create schema public;

-- покупатели
create table users (
    id serial primary key,
    name varchar(100) not null,
    balance numeric default 0.00,
    check (balance >= 0) 
);

-- категории товаров
create table categories (
    id serial primary key,
    name varchar(50) not null unique
);

-- ифномация о продуктах
create table products (
    id serial primary key,
    category_id int references categories (id),
    name varchar(100) not null,
    title text not null,
    price numeric not null,
    now_amount int not null,
    check (now_amount >= 0),
    check (price >= 0)
);

create index products_category_id on products (category_id);

--ифнормация о заказе
create table orders (
    id serial primary key,
    user_id int references users(id),
    created_at timestamp default current_timestamp,
    status varchar(50) default 'created',
    check (status in ('created', 'prepared', 'finish', 'delivery', 'delivered'))
);

create index orders_user_id_index on orders (user_id);

-- таблица связи many-to-many между товарами и заказами
create table order_items(
    order_id int not null references orders (id) on delete cascade,
    product_id int not null references products (id) on delete cascade,
    amount int not null,
    first_price numeric not null,
    primary key (order_id, product_id),
    check (amount > 0),
    check (first_price >= 0)
);

create table cart(
    user_id int references users (id) unique on delete cascade,
    product_id int references products (id) on delete cascade,
    amount int,
    primary key (user_id, product_id)
);