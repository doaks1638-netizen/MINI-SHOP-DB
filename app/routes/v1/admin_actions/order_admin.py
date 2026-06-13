from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Order, User
from app.database import DBsession
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload
from app.models.enums import OrderStatus
from app.services import update_amount, debit_funds
from app.filters import DateFilter
from app.schemas import OrderStatusEdit, OrderRelDTO, AdminOrderDTO
from uuid import UUID
from app.routes import page_number
from app.routes import get_current_admin
from typing import Annotated

admin_order_router = APIRouter(
    prefix="/admin/orders", tags=["ADMIN"], dependencies=[Depends(get_current_admin)]
)


@admin_order_router.get("/", response_model=list[AdminOrderDTO])
async def get_all_orders(
    db: DBsession,
    page: page_number,
    date_filter: Annotated[DateFilter, Query()] = DateFilter.new,
    status_filter: Annotated[list[OrderStatus] | None, Query()] = None,
):
    stmt = select(
        Order.product_id,
        Order.amount,
        Order.id,
        Order.status,
        Order.created_at,
        User.is_active.label("is_user_active"),
    ).join(User, User.id == Order.user_id)

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


@admin_order_router.get("/{order_id}", response_model=OrderRelDTO)
async def get_order_info(db: DBsession, order_id: UUID):
    stmt = (
        select(Order).options(selectinload(Order.product)).where(Order.id == order_id)
    )
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@admin_order_router.patch("/{order_id}")
async def change_order(db: DBsession, new_status: OrderStatusEdit, order_id: UUID):
    stmt = (
        update(Order)
        .where(Order.id == order_id)
        .values(status=new_status.status)
        .returning(Order.id)
    )
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.commit()


@admin_order_router.delete("/{order_id}", status_code=204)
async def delete_order(db: DBsession, order_id: UUID):
    stmt = select(Order).where(Order.id == order_id)
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = OrderStatus.cancelled
    await update_amount(db, order.product_id, order.amount)
    await debit_funds(db, order.user_id, (order.price_for_one * order.amount))
    await db.commit()
