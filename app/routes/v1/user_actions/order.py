from fastapi import APIRouter, HTTPException, Depends
from app.database import DBsession
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from app.models.order import Order
from app.models.product import Product
from app.models.order_item import OrderItem
from app.models.order_status_enum import OrderStatus
from app.services import update_amount, debit_funds
from app.schemas import OrderCreateRequest, OrderRelDTO
from app.models.categories import Category
from app.models.user import User
from uuid import UUID
from typing import Annotated
from app.routes.dependencies import get_current_user
from decimal import Decimal

order_router = APIRouter(prefix="/orders", tags=["ORDERS"])


@order_router.post("/", status_code=201)
async def create_order(
    db: DBsession,
    order: OrderCreateRequest,
    user: Annotated[User, Depends(get_current_user)],
):

    if not order.items:
        raise HTTPException(status_code=400, detail="The order must contain items!")

    new_order = Order(user_id=user.id)
    db.add(new_order)
    await db.flush()

    products_id = {item.product_id for item in order.items}
    order_objects_stmt = (
        select(Product)
        .join(Category, Product.category_id == Category.id)
        .where(Product.is_active == True)
        .where(Category.is_active == True)
        .where(Product.id.in_(products_id))
    )
    rez = await db.scalars(order_objects_stmt)
    order_objects = rez.all()

    products = {p.id: p for p in order_objects}

    if len(products_id) != len(products):
        raise HTTPException(
            status_code=404, detail="The price of some orders not found"
        )

    insert_data = []
    total_order_price = Decimal("0")

    for item in order.items:
        db_product = products[item.product_id]

        await update_amount(db, item.product_id, -item.amount)

        actual_price = db_product.price

        data = {
            "order_id": new_order.id,
            "amount": item.amount,
            "product_id": item.product_id,
            "price_for_one": actual_price,
        }

        insert_data.append(data)
        total_order_price += actual_price * item.amount

    insert_stmt = insert(OrderItem).values(insert_data)
    new_order.total_price = total_order_price

    await debit_funds(db, user.id, -total_order_price)

    await db.execute(insert_stmt)
    await db.commit()

    return {"order_id": new_order.id, "total_price": total_order_price}


@order_router.get("/me/{order_id}", response_model=OrderRelDTO)
async def get_my_order_info(
    db: DBsession, order_id: UUID, user: Annotated[User, Depends(get_current_user)]
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.user_id == user.id)
    )
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@order_router.delete("/me/{order_id}", status_code=204)
async def delete_my_order(
    db: DBsession, order_id: UUID, user: Annotated[User, Depends(get_current_user)]
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == user.id,
            Order.status != OrderStatus.cancelled,
        )
    )
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for order_item in order.items:
        await update_amount(db, order_item.product_id, order_item.amount)
    order.status = OrderStatus.cancelled
    await debit_funds(db, order.user_id, order.total_price)
    await db.commit()
