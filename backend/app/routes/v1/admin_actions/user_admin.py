from fastapi import APIRouter, Depends, Query
from app.models import Order, User
from app.db.database import DBsession
from app.schemas import UserPatch, AdminUserDTO, AdminUserDTOCount, AdminOrderDTO
from sqlalchemy import select, func
from app.routes import get_current_admin, page_number
from app.services import user_depends
from app.models.enums import UserRole, UserStatus
from typing import Annotated

admin_user_router = APIRouter(
    prefix="/admin/users", dependencies=[Depends(get_current_admin)], tags=["ADMIN"]
)


@admin_user_router.get("/", response_model=list[AdminUserDTOCount])
async def get_users(
    db: DBsession,
    page: page_number = 1,
    roles: Annotated[list[UserRole] | None, Query()] = None,
):
    stmt = (
        select(
            User.id,
            User.name,
            func.count(Order.id).label("orders_count"),
            User.status.label("user_status"),
        )
        .outerjoin(Order)
        .group_by(User.id, User.name, User.status)
    )

    if roles:
        stmt = stmt.where(User.role.in_(roles))

    stmt = stmt.limit(30).offset(30 * (page - 1))

    users = (await db.execute(stmt)).mappings().all()
    return users


@admin_user_router.get("/{user_id}", response_model=AdminUserDTO)
async def get_user(user: user_depends):
    return user


@admin_user_router.patch("/{user_id}", response_model=AdminUserDTO)
async def change_user_profile(
    db: DBsession, new_profile: UserPatch, user: user_depends
):
    user.name = new_profile.name
    await db.commit()
    await db.refresh(user)

    return user


@admin_user_router.delete("/{user_id}", status_code=204)
async def delete_user(db: DBsession, user: user_depends):
    user.status = UserStatus.deleted
    await db.commit()


@admin_user_router.get("/{user_id}/orders", response_model=list[AdminOrderDTO])
async def get_user_orders(db: DBsession, user: user_depends, page: page_number = 1):
    orders_stmt = (
        select(
            Order.product_id,
            Order.amount,
            Order.id,
            Order.status,
            Order.created_at,
            User.status.label("user_status"),
        )
        .join(User, User.id == user.id)
        .where(Order.user_id == user.id)
        .limit(30)
        .offset(30 * (page - 1))
    )
    orders = await db.execute(orders_stmt)
    return orders.mappings().all()
