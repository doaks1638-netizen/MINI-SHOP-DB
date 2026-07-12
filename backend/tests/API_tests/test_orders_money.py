from app.models import CartItem, Order, User, Payment
from app.models.enums import OrderStatus, PaymentStatus
from fastapi import status
from uuid6 import uuid7
from sqlalchemy import select
import pytest


@pytest.fixture(scope="function")
async def new_product(auth_admin):
    id, auth_admin = auth_admin
    json_data = {
        "name": f"name_{uuid7()}",
    }
    rez = await auth_admin.post("/api/v1/admin/categories/", json=json_data)
    category_id = rez.json()["id"]

    async def post_form_data(now_amount: str = "100"):
        form_data = {
            "category_id": category_id,
            "name": f"name_{uuid7()}",
            "price": "100.0",
            "now_amount": now_amount,
            "is_active": "true",
        }
        rez = await auth_admin.post("/api/v1/admin/products/", data=form_data)
        return rez.json()

    return post_form_data


class TestCarts:
    async def test_post_product_to_cart(self, auth_client, db, new_product):
        id, auth_client = auth_client
        product = await new_product()
        product_id = product["id"]
        product_info = {"product_id": product_id, "amount": 1}
        rez = await auth_client.post("/api/v1/cart/", json=product_info)
        assert rez.status_code == status.HTTP_201_CREATED
        assert await db.scalar(
            select(CartItem).where(
                CartItem.user_id == id,
                CartItem.product_id == product_id,
                CartItem.amount == 1,
            )
        )


class TestOrders:
    async def test_create_order(self, auth_client, db, new_product):
        id, auth_client = auth_client
        product = await new_product()
        product_id = product["id"]
        user = await db.scalar(select(User).where(User.id == id))
        user.balance = 1000
        await db.commit()

        order_info = {"product_id": product_id, "amount": 1}
        rez = await auth_client.post("/api/v1/orders/", json=order_info)
        assert rez.status_code == status.HTTP_201_CREATED
        assert await db.scalar(
            select(Order).where(
                Order.user_id == id,
                Order.product_id == product_id,
                Order.amount == 1,
                Order.status == OrderStatus.created,
            )
        )

    async def test_create_order_fail(self, auth_client, new_product, db):
        id, auth_client = auth_client
        user = await db.scalar(select(User).where(User.id == id))
        user.balance = 1000
        await db.commit()
        product = await new_product(now_amount="0")
        product_id = product["id"]
        order_info = {"product_id": product_id, "amount": 1}
        rez = await auth_client.post("/api/v1/orders/", json=order_info)
        assert rez.status_code == status.HTTP_409_CONFLICT

    async def test_сancel_order(self, auth_client, db, new_product):
        id, auth_client = auth_client
        product = await new_product()
        product_id = product["id"]
        user = await db.scalar(select(User).where(User.id == id))
        user.balance = 1000
        await db.commit()
        order_info = {"product_id": product_id, "amount": 1}
        response = await auth_client.post("/api/v1/orders/", json=order_info)
        order_id = response.json()["id"]
        await auth_client.delete(f"/api/v1/orders/me/{order_id}")
        await db.refresh(user)
        assert user.balance == 1000

    async def test_сancel_order_admin(self, auth_admin, db, new_product):
        id, auth_admin = auth_admin
        product = await new_product()
        product_id = product["id"]
        user = await db.scalar(select(User).where(User.id == id))
        user.balance = 1000
        await db.commit()
        order_info = {"product_id": product_id, "amount": 1}
        response = await auth_admin.post("/api/v1/orders/", json=order_info)
        order_id = response.json()["id"]
        await auth_admin.delete(f"/api/v1/admin/orders/{order_id}")
        await db.refresh(user)
        assert user.balance == 1000

    async def test_сancel_order_two_times(self, auth_client, db, new_product):
        id, auth_client = auth_client
        product = await new_product()
        product_id = product["id"]
        user = await db.scalar(select(User).where(User.id == id))
        user.balance = 1000
        await db.commit()
        order_info = {"product_id": product_id, "amount": 1}
        response = await auth_client.post("/api/v1/orders/", json=order_info)
        order_id = response.json()["id"]
        await auth_client.delete(f"/api/v1/orders/me/{order_id}")
        await auth_client.delete(f"/api/v1/orders/me/{order_id}")
        await db.refresh(user)
        assert user.balance == 1000


class TestPayment:
    async def test_yookassa_webhook(self, auth_client, db):
        id, auth_client = auth_client
        top_up_amount = 500

        user = await db.scalar(select(User).where(User.id == id))
        user.balance = 1000
        payment = Payment(
            user_id=id,
            amount=top_up_amount,
            yookassa_id="test_yookassa_payment_id_12345",
            status=PaymentStatus.pending,
        )
        db.add(payment)
        await db.commit()

        webhook_payload = {
            "type": "notification",
            "event": "payment.succeeded",
            "object": {
                "id": "test_yookassa_payment_id_12345",
                "status": "succeeded",
                "amount": {"value": f"{top_up_amount:.2f}", "currency": "RUB"},
            },
        }
        webhook_headers = {"x-real-ip": "77.75.156.11"}
        result = await auth_client.post(
            "/api/v1/payments/yookassa/webhook",
            json=webhook_payload,
            headers=webhook_headers,
        )
        assert result.status_code == status.HTTP_200_OK
        assert await db.scalar(select(User.balance).where(User.id == id)) == 1500
