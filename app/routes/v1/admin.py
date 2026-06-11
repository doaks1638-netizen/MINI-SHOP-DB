from fastapi import APIRouter, Depends
from app.database import DBsession
from app.schemas import (
    UserPatch,
    UserDTO,
    OrderDTO,
)
from app.models.order import Order
from sqlalchemy import select
from app.routes.dependencies import (
    get_current_admin,
)
from app.services import user_depens

admin_router = APIRouter(
    prefix="/admin/users", dependencies=[Depends(get_current_admin)]
)


@admin_router.get("/{user_id}", response_model=UserDTO)
async def get_user(user: user_depens):
    return user


@admin_router.patch("/{user_id}", response_model=UserDTO)
async def change_user_profile(db: DBsession, new_profile: UserPatch, user: user_depens):
    user.name = new_profile.name
    await db.commit()
    await db.refresh(user)

    return user


@admin_router.delete("/{user_id}", status_code=204)
async def delete_user(db: DBsession, user: user_depens):
    user.is_active = False
    await db.commit()


@admin_router.get("/{user_id}/orders", response_model=list[OrderDTO])
async def get_user_orders(db: DBsession, user: user_depens):
    orders_stmt = select(Order).where(Order.user_id == user.id)
    orders = await db.scalars(orders_stmt)
    return orders
