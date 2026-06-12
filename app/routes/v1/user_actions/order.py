from fastapi import APIRouter, HTTPException, Depends
from app.database import DBsession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.models.order import Order
from app.models.product import Product
from app.models.order_status_enum import OrderStatus
from app.services import debit_funds
from app.schemas import OrderCreate, OrderDTO, OrderRelDTO
from app.models.user import User
from app.models.cart_item import CartItem
from uuid import UUID
from typing import Annotated
from app.routes import get_current_user

order_router = APIRouter(prefix="/orders", tags=["ORDERS"])


@order_router.post("/", status_code=201, response_model=OrderDTO)
async def create_order(
    db: DBsession,
    order: OrderCreate,
    user: Annotated[User, Depends(get_current_user)],
):

    product = await db.scalar(
        select(Product).where(Product.id == order.product_id, Product.is_active == True)
    )

    if not product:
        raise HTTPException(404, detail="Product not found")

    actual_price = product.price

    new_order = Order(user_id=user.id, price_for_one=actual_price, **order.model_dump())
    db.add(new_order)

    await debit_funds(db, user.id, -(actual_price * order.amount))

    await db.commit()

    await db.refresh(new_order)

    return new_order


@order_router.get("/me/{order_id}", response_model=OrderRelDTO)
async def get_my_order_info(
    db: DBsession, order_id: UUID, user: Annotated[User, Depends(get_current_user)]
):
    stmt = (
        select(Order)
        .options(selectinload(Order.product))
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
    stmt = select(Order).where(
        Order.id == order_id,
        Order.user_id == user.id,
        Order.status != OrderStatus.cancelled,
    )
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = OrderStatus.cancelled
    await debit_funds(db, order.user_id, (order.price_for_one * order.amount))
    await db.commit()


@order_router.post("/cart", status_code=201)
async def create_order_from_cart(
    db: DBsession, user: Annotated[User, Depends(get_current_user)]
):
    result = await db.scalars(select(CartItem).where(CartItem.user_id == user.id))
    cart_items = result.all()

    if not cart_items:
        raise HTTPException(404, detail="The cart is empty")

    for item in cart_items:
        await create_order(
            db,
            OrderCreate(product_id=item.product_id, amount=item.amount),
            user=user,
        )
        await db.execute(delete(CartItem).where(CartItem.user_id == user.id))

    await db.commit()

    # This is how deletion was intended;
    # the server simply has no reason to store past items in the user's shopping cart.
