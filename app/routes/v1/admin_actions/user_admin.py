from fastapi import APIRouter, HTTPException, Depends
from app.database import DBsession
from app.schemas import UserPatch, UserDTO, OrderDTO, UserCreate
from app.models.order import Order
from app.models.user import User
from sqlalchemy import select
from app.routes.dependencies import get_current_admin
from app.services import user_depends, create_hash_password

admin_user_router = APIRouter(
    prefix="/admin/users", dependencies=[Depends(get_current_admin)], tags=["ADMIN"]
)


@admin_user_router.get("/{user_id}", response_model=UserDTO)
async def get_user(user: user_depends):
    return user


@admin_user_router.patch("/{user_id}", response_model=UserDTO)
async def change_user_profile(db: DBsession, new_profile: UserPatch, user: user_depends):
    user.name = new_profile.name
    await db.commit()
    await db.refresh(user)

    return user


@admin_user_router.delete("/{user_id}", status_code=204)
async def delete_user(db: DBsession, user: user_depends):
    user.is_active = False
    await db.commit()


@admin_user_router.get("/{user_id}/orders", response_model=list[OrderDTO])
async def get_user_orders(db: DBsession, user: user_depends):
    orders_stmt = select(Order).where(Order.user_id == user.id)
    orders = await db.scalars(orders_stmt)
    return orders


@admin_user_router.post("/", response_model=UserDTO)
async def create_user(db: DBsession, new_user: UserCreate):
    same_user = select(User).where(User.email == new_user.email)
    if await db.scalar(same_user):
        raise HTTPException(400, detail="User already exists")
    new_user = User(
        name=new_user.name,
        email=new_user.email,
        hash_password=create_hash_password(new_user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
