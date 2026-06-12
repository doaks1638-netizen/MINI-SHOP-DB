from fastapi import APIRouter, Depends
from app.database import DBsession
from app.routes import page_number
from app.schemas import UserPatch, UserDTO, OrderDTO, BalanceUpdate, NewBalance
from app.models.user import User
from app.models.order import Order
from sqlalchemy import select
from typing import Annotated
from app.routes import get_current_user

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
    user.picture = new_profile.picture
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
        select(Order).where(Order.user_id == user.id).limit(30).offset(30 * (page - 1))
    )
    orders = await db.scalars(orders_stmt)
    return orders


@user_router.post("/me/balance", response_model=NewBalance)
async def update_balance(
    db: DBsession,
    update_schema: BalanceUpdate,
    user: Annotated[User, Depends(get_current_user)],
):
    """
    For now, the scheme is implemented with any amount of money; the YUKassa API will be added later.
    Stay tuned for updates!
    """
    user.balance += update_schema.update_amount
    await db.commit()
    await db.refresh(user)
    return NewBalance(balance=user.balance)
