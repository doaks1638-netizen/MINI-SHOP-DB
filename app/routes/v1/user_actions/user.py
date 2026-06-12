from fastapi import APIRouter, Depends
from app.database import DBsession
from app.routes import page_number
from app.schemas import (
    UserPatch,
    UserDTO,
    OrderDTO,
)
from app.models.user import User
from app.models.order import Order
from sqlalchemy import select
from typing import Annotated
from app.routes.dependencies import get_current_user

user_router = APIRouter(prefix="/users", tags=["USERS"])


@user_router.get("/me", response_model=UserDTO)
async def get_me(user: Annotated[User, Depends(get_current_user)]):
    return user


@user_router.patch("/me", response_model=UserDTO)
async def change_my_profile(
    db: DBsession,
    new_profile: UserPatch,
    user: Annotated[User, Depends(get_current_user)],
):
    user.name = new_profile.name
    await db.commit()
    await db.refresh(user)

    return user


@user_router.delete("/me", status_code=204)
async def delete_user(db: DBsession, user: Annotated[User, Depends(get_current_user)]):
    user.is_active = False
    await db.commit()


@user_router.get("/me/orders", response_model=list[OrderDTO])
async def get_user_orders(
    db: DBsession,
    page: page_number,
    user: Annotated[User, Depends(get_current_user)],
):
    orders_stmt = (
        select(Order)
        .where(Order.user_id == user.id)
        .limit(30)
        .offset(30 * (page - 1))
    )
    orders = await db.scalars(orders_stmt)
    return orders
