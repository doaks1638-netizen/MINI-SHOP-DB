from app.models import User, CartItem
from sqlalchemy import select
from fastapi import status
import pytest
from uuid6 import uuid7


@pytest.fixture(scope="function")
async def create_products(db, category_saver, product_saver):
    category_id = await category_saver()
    products = []
    products.append(
        await product_saver(
            category_id=category_id,
            name='TEST Sony Телевизор 65XR65X90L 65" 4K Full Array LED, черный',
            price=1200,
            now_amount=1,
            description="Full Array LED экран, процессор Cognitive Processor XR, идеален для PS5.",
        )
    )

    products.append(
        await product_saver(
            category_id=category_id,
            name="TEST Samsung Смартфон Galaxy S24 256GB, серый",
            price=950,
            now_amount=1,
            description="Дисплей Dynamic AMOLED 2X, функции Galaxy AI, тройная камера с ИИ.",
        )
    )

    products.append(
        await product_saver(
            category_id=category_id,
            name='TEST Lenovo Ноутбук IdeaPad Slim 5 16IAH8 16", серебристый',
            price=750,
            now_amount=2,
            description="Intel Core i7, 16GB RAM, 1TB SSD, прочный алюминиевый корпус.",
        )
    )
    return products


class TestCart:
    async def test_create_order_from_cart(self, auth_client, db, create_products):
        id, auth_client = auth_client
        user = await db.scalar(select(User).where(User.id == id))
        user.balance = 10000
        await db.commit()
        # Add 2 items with a standard quantity; for the 3rd, set a higher stock level.
        for product in create_products:
            product_json = {
                "product_id": f"{product.id}",
                "amount": product.now_amount,
            }
            await auth_client.post("/api/v1/cart/", json=product_json)
        response = await auth_client.get("/api/v1/cart/")
        print(response.headers, response.json(), response.status_code)
        assert all(x["status"] == "in_stock" for x in response.json())
        response = await auth_client.post("/api/v1/orders/cart")
        assert response.status_code == status.HTTP_201_CREATED
        assert (
            await db.scalar(select(User.balance).where(User.id == id))
        ) < user.balance
        assert (
            len(
                (await db.execute(select(CartItem).where(CartItem.user_id == id)))
                .scalars()
                .all()
            )
            == 0
        )

    async def test_create_order_from_cart_with_out_of_stock(
        self, auth_client, db, create_products
    ):
        id, auth_client = auth_client
        user = await db.scalar(select(User).where(User.id == id))
        user.balance = 10007890
        await db.commit()
        for number, product in enumerate(create_products, start=-1):
            product_json = {
                "product_id": f"{product.id}",
                "amount": product.now_amount + number,
            }
            await auth_client.post("/api/v1/cart/", json=product_json)
        response = await auth_client.get("/api/v1/cart/")
        print(response.headers, response.json(), response.status_code)
        assert any(x["status"] == "out_of_stock" for x in response.json())
        response = await auth_client.post("/api/v1/orders/cart")
        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_create_order_from_cart_witр_low_balance(
        self, auth_client, db, create_products
    ):
        id, auth_client = auth_client
        for product in create_products:
            product_json = {
                "product_id": f"{product.id}",
                "amount": product.now_amount,
            }
            await auth_client.post("/api/v1/cart/", json=product_json)
        response = await auth_client.get("/api/v1/cart/")
        print(response.headers, response.json(), response.status_code)
        response = await auth_client.post("/api/v1/orders/cart")
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED
