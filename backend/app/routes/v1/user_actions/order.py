from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import CartItem, Order, Product, User
from backend.app.db.database import DBsession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.models.enums import OrderStatus
from app.services import debit_funds, update_amount
from app.schemas import OrderCreate, OrderDTO, OrderRelDTO
from uuid import UUID
from typing import Annotated
from app.routes import page_number
from sqlalchemy import desc
from app.routes import get_current_user
from app.filters import DateFilter

order_router = APIRouter(prefix="/orders", tags=["ORDERS"])


async def create_order(db: DBsession, order: OrderCreate, user_id: UUID):

    product = await db.scalar(
        select(Product).where(Product.id == order.product_id, Product.is_active == True)
    )

    if not product:
        return

    actual_price = product.price

    await update_amount(db, order.product_id, -order.amount)

    await debit_funds(db, user_id, -(actual_price * order.amount))

    new_order = Order(user_id=user_id, price_for_one=actual_price, **order.model_dump())
    db.add(new_order)

    await db.flush()

    return new_order


@order_router.post("/", status_code=201, response_model=OrderDTO)
async def create_one_order(
    db: DBsession,
    order: OrderCreate,
    user: Annotated[User, Depends(get_current_user)],
):
    rez = await create_order(db, order, user.id)

    await db.commit()
    await db.refresh(rez)
    return rez


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
    await update_amount(db, order.product_id, order.amount)
    await debit_funds(db, order.user_id, (order.price_for_one * order.amount))
    order.status = OrderStatus.cancelled
    await db.commit()


@order_router.post("/cart", status_code=201)
async def create_order_from_cart(
    db: DBsession, user: Annotated[User, Depends(get_current_user)]
):
    result = await db.scalars(select(CartItem).where(CartItem.user_id == user.id))
    cart_items = result.all()

    if not cart_items:
        raise HTTPException(404, detail="The cart is empty")

    orders_to_create = [
        OrderCreate(product_id=item.product_id, amount=item.amount)
        for item in cart_items
    ]

    for order_create in orders_to_create:
        await create_order(db, order_create, user_id=user.id)

    await db.execute(delete(CartItem).where(CartItem.user_id == user.id))
    await db.commit()

    # This is how deletion was intended;
    # the server simply has no reason to store past items in the user's shopping cart.


@order_router.get("/", response_model=list[OrderDTO])
async def get_all_orders(
    db: DBsession,
    user: Annotated[User, Depends(get_current_user)],
    page: page_number = 1,
    date_filter: Annotated[DateFilter, Query()] = DateFilter.new,
    status_filter: Annotated[list[OrderStatus] | None, Query()] = None,
):
    stmt = (
        select(
            Order.product_id,
            Order.amount,
            Order.id,
            Order.status,
            Order.created_at,
        )
        .join(User, User.id == Order.user_id)
        .join(Product, Product.id == Order.product_id)
        .where(User.id == user.id)
    )

    if status_filter:
        stmt = stmt.where(Order.status.in_(status_filter))

    match date_filter:
        case DateFilter.new:
            stmt = stmt.order_by(desc(Order.created_at))
        case DateFilter.old:
            stmt = stmt.order_by(Order.created_at)

    stmt = stmt.limit(30).offset(30 * (page - 1))

    rez = await db.execute(stmt)
    return rez.mappings().all()
