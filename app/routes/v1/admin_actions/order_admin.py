from fastapi import APIRouter, HTTPException, Depends
from app.database import DBsession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.models.order import Order
from app.models.user import User
from app.models.order_status_enum import OrderStatus
from app.services import update_amount, debit_funds
from app.schemas import OrderDTO, OrderStatusEdit, OrderRelDTO
from uuid import UUID
from app.routes import page_number
from app.routes.dependencies import get_current_admin

admin_order_router = APIRouter(
    prefix="/admin/orders", tags=["ADMIN"], dependencies=[Depends(get_current_admin)]
)


@admin_order_router.get("/", response_model=list[OrderDTO])
async def get_all_orders(db: DBsession, page: page_number):
    stmt = (
        select(Order)
        .join(User, User.id == Order.user_id)
        .where(User.is_active == True, Order.status != OrderStatus.cancelled)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.scalars(stmt)
    return rez.all()


@admin_order_router.get("/{order_id}", response_model=OrderRelDTO)
async def get_order_info(db: DBsession, order_id: UUID):
    stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@admin_order_router.patch("/{order_id}")
async def change_order(db: DBsession, new_status: OrderStatusEdit, order_id: UUID):
    stmt = (
        update(Order)
        .where(Order.user_id == User.id)
        .where(Order.id == order_id)
        .where(User.is_active == True)
        .values(status=new_status.status)
        .returning(Order.id)
    )
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.commit()


@admin_order_router.delete("/{order_id}", status_code=204)
async def delete_order(db: DBsession, order_id: UUID):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .join(User, User.id == Order.user_id)
        .where(User.is_active == True)
        .where(Order.id == order_id)
    )
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for order_item in order.items:
        await update_amount(db, order_item.product_id, order_item.amount)
    order.status = OrderStatus.cancelled
    await debit_funds(db, order.user_id, order.total_price)
    await db.commit()

