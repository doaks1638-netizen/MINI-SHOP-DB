# Mini Shop DB

Учебный backend-проект интернет-магазина на Python + PostgreSQL.

Проект сделан как тренировка:

* работы с PostgreSQL;
* транзакций и блокировок;
* разделения слоев приложения;
* repository/service architecture;
* работы с psycopg3;
* бизнес-логики без ORM.

---

## Стек

* Python 3.12+
* PostgreSQL
* psycopg3
* python-dotenv

---

## Возможности

### Пользователи

* создание пользователя;
* удаление пользователя;
* просмотр пользователей;
* пополнение баланса.

### Товары

* создание товара;
* удаление товара;
* просмотр товаров;
* изменение цены;
* изменение количества товара.

### Категории

* создание категорий;
* просмотр категорий.

### Корзина

* добавление товара в корзину;
* удаление товара из корзины;
* просмотр корзины пользователя.

### Заказы

* покупка товара напрямую;
* оформление заказа из корзины;
* создание order items;
* автоматическое списание товаров;
* автоматическое списание денег.

---

## Архитектура проекта

```text
Mini_Shop_DB/
│
├── app/
│   ├── config.py        # env-конфиг
│   ├── db.py            # подключение к PostgreSQL
│   ├── repositories.py  # SQL-запросы
│   ├── services.py      # бизнес-логика и транзакции
│   └── __init__.py
│
├── database/
│   └── schema.sql       # схема БД
│
├── main.py
└── .env
```

---

## Разделение ответственности

### repositories.py

Содержит только SQL-запросы:

* SELECT
* INSERT
* UPDATE
* DELETE

Repository-слой не содержит бизнес-логики.

Пример:

```python
ProductRepository.get_by_id(conn, product_id)
```

---

### services.py

Содержит:

* проверки;
* транзакции;
* бизнес-логику;
* обработку ошибок;
* orchestration между repository.

Пример:

```python
buy_product_now(user_id, product_id, amount)
```

Именно service-слой:

* проверяет баланс;
* проверяет остаток товара;
* блокирует строки через FOR UPDATE;
* обновляет данные;
* создает заказ.

---

## Подключение к БД

### .env

```env
HOST=localhost
PORT=5432
DBNAME=mini_shop
USER=postgres
PASSWORD=postgres
```

---

## Установка

### 1. Клонирование

```bash
git clone <repo_url>
cd Mini_Shop_DB
```

---

### 2. Устранение зависимостей

```bash
pip install uv
uv sync
```


### 3. Создание базы

```sql
CREATE DATABASE mini_shop;
```

---

### 4. Применение схемы

```bash
psql -U postgres -d mini_shop -f database/schema.sql
```

---

## Работа с транзакциями

В проекте используется:

* `with get_connect() as conn:`
* автоматический commit;
* rollback при ошибках;
* `SELECT ... FOR UPDATE` для защиты от race condition.

Пример:

```python
product = ProductRepository.get_by_id(
    conn,
    product_id,
    for_update=True
)
```

Это блокирует строку товара до конца транзакции.

---

## Возможные улучшения

* CLI-интерфейс;
* pytest-тесты;
* logging;
* Docker;
* миграции через Alembic;
* SQLAlchemy version;
* FastAPI API;
* авторизация;
* async psycopg.

---

## Пример использования

```python
from services import buy_product_now

buy_product_now(
    user_id=1,
    product_id=3,
    amount=2
)
```

---

## Идея проекта

Проект специально написан без ORM, чтобы:

* понимать SQL;
* понимать транзакции;
* видеть реальные запросы;
* научиться проектировать backend-логику вручную.

Это учебный проект для практики backend + PostgreSQL.
