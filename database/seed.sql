# тестовые данные для заполнения

-- Заполнение категорий
INSERT INTO categories (name) VALUES
('Electronics'),
('Clothing'),
('Food'),
('Books'),
('Sport');

-- Заполнение пользователей
INSERT INTO users (name, balance) VALUES
('Alice Johnson', 1500.00),
('Bob Smith', 320.50),
('Carol White', 870.00),
('David Brown', 50.00),
('Eva Green', 2200.75);

-- Заполнение товаров (добавлен столбец now_amount)
INSERT INTO products (category_id, name, title, now_amount) VALUES
(1, 'iPhone 14',             'Смартфон Apple iPhone 14 128GB',              15),
(1, 'Samsung TV 55"',        'Телевизор Samsung QLED 55 дюймов',             8),
(1, 'AirPods Pro',           'Беспроводные наушники Apple AirPods Pro 2',   30),
(2, 'Nike T-Shirt',          'Футболка Nike Dri-FIT размер M',               50),
(2, 'Levi''s 501',           'Джинсы Levi''s 501 Original W32 L32',         20),
(3, 'Organic Coffee',        'Кофе арабика молотый 500г',                   100),
(3, 'Dark Chocolate',        'Шоколад горький 85% 100г',                    200),
(4, 'Clean Code',            'Clean Code by Robert C. Martin',               12),
(4, 'The Pragmatic Programmer', 'The Pragmatic Programmer by D. Thomas',    10),
(5, 'Yoga Mat',              'Коврик для йоги 6мм нескользящий',             35);

-- Заполнение заказов
INSERT INTO orders (user_id, created_at, status) VALUES
(1, '2024-11-01 10:30:00', 'finish'),
(1, '2024-12-15 14:00:00', 'delivery'),
(2, '2024-12-20 09:15:00', 'prepared'),
(3, '2025-01-05 16:45:00', 'created'),
(4, '2025-01-10 11:00:00', 'finish'),
(5, '2025-01-12 13:30:00', 'created');

-- Заполнение позиций заказов
INSERT INTO order_items (order_id, product_id, amount, first_price) VALUES
(1, 1, 1,  999.00),
(1, 3, 2,  249.00),
(2, 2, 1, 1200.00),
(3, 4, 3,   29.99),
(3, 6, 2,   14.50),
(4, 8, 1,   35.00),
(4, 9, 1,   40.00),
(5, 5, 2,   59.99),
(5, 7, 4,    4.50),
(6, 10, 1,  25.00),
(6, 6, 3,   14.50);