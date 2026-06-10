from fastapi import APIRouter, HTTPException
from app.database import DBsession
from app.routes.dependencies import page_number
from app.schemas import UserRelCount, UserPatch, UserDTO, OrderDTO, UserCreate
from app.models.user import User
from app.models.order import Order
from app.services import user_depens
from sqlalchemy import select, func, insert
from uuid import UUID

user_router = APIRouter()


@user_router.get("/users", response_model=list[UserRelCount])
async def get_users(db: DBsession, page: page_number):
    stmt = (
        select(
            User.id,
            User.name,
            User.balance,
            func.count(Order.id).label("orders_count"),
        )
        .outerjoin(Order)
        .where(User.is_active == True)
        .group_by(User.id, User.name, User.balance)
        .limit(30)
        .offset(30 * (page - 1))
    )
    users = (await db.execute(stmt)).mappings().all()
    return [UserRelCount.model_validate(x) for x in users]


@user_router.post("/users", status_code=201)
async def create_new_user(db: DBsession, new_user: UserCreate):
    stmt = insert(User).values(**new_user.model_dump())
    await db.execute(stmt)
    await db.commit()


@user_router.get("/users/{user_id}", response_model=UserDTO)
async def get_user(user: user_depens):
    return UserDTO.model_validate(user)


@user_router.patch("/users/{user_id}")
async def change_user_profile(db: DBsession, new_profile: UserPatch, user: user_depens):
    user.name = new_profile.name
    await db.commit()


@user_router.delete("/users/{user_id}", status_code=204)
async def delete_user(db: DBsession, user: user_depens):
    user.is_active = False
    await db.commit()


@user_router.get("/users/{user_id}/orders", response_model=list[OrderDTO])
async def get_user_orders(db: DBsession, user_id: UUID):
    user_stmt = (
        select(1)
        .select_from(User)
        .where(User.id == user_id)
        .where(User.is_active == True)
    )
    user_exists = await db.scalar(user_stmt)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    orders_stmt = select(Order).where(Order.user_id == user_id)
    orders = await db.scalars(orders_stmt)
    return [OrderDTO.model_validate(x) for x in orders]
