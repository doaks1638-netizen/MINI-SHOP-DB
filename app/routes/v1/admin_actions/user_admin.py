from fastapi import APIRouter, Depends
from app.database import DBsession
from app.schemas import UserPatch, UserDTO, OrderDTO, UserDTOCount
from app.models.order import Order
from app.models.user import User
from sqlalchemy import select, func
from app.routes import get_current_admin, page_number
from app.services import user_depends

admin_user_router = APIRouter(
    prefix="/admin/users", dependencies=[Depends(get_current_admin)], tags=["ADMIN"]
)


@admin_user_router.get("/", response_model=list[UserDTOCount])
async def get_users(db: DBsession, page: page_number):
    stmt = (
        select(
            User.name,
            func.count(Order.id).label("orders_count"),
        )
        .outerjoin(Order)
        .where(User.is_active == True)
        .group_by(User.id, User.name, User.balance, User.email, User.role)
        .limit(30)
        .offset(30 * (page - 1))
    )
    users = (await db.execute(stmt)).mappings().all()
    return users


@admin_user_router.get("/{user_id}", response_model=UserDTO)
async def get_user(user: user_depends):
    return user


@admin_user_router.patch("/{user_id}", response_model=UserDTO)
async def change_user_profile(
    db: DBsession, new_profile: UserPatch, user: user_depends
):
    user.name = new_profile.name
    await db.commit()
    await db.refresh(user)

    return user


@admin_user_router.delete("/{user_id}", status_code=204)
async def delete_user(db: DBsession, user: user_depends):
    user.is_active = False
    await db.commit()


@admin_user_router.get("/{user_id}/orders", response_model=list[OrderDTO])
async def get_user_orders(db: DBsession, page: page_number, user: user_depends):
    orders_stmt = (
        select(Order).where(Order.user_id == user.id).limit(30).offset(30 * (page - 1))
    )
    orders = await db.scalars(orders_stmt)
    return orders.all()
