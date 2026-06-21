from fastapi import APIRouter, Depends, HTTPException
from app.models import User, Payment
from app.database import DBsession
from app.schemas import (
    UserPatch,
    UserDTO,
    BalanceUpdate,
)
from typing import Annotated
from app.routes import get_current_user
from app.services import create_yookaassa_payment

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


@user_router.post("/me/balance")
async def update_balance(
    db: DBsession,
    update_schema: BalanceUpdate,
    user: Annotated[User, Depends(get_current_user)],
):
    new_payment = Payment(
        user_id=user.id,
        amount=update_schema.update_amount,
    )
    db.add(new_payment)
    await db.flush()

    try:
        yookassa_id, new_url = await create_yookaassa_payment(
            db, new_payment.amount, new_payment.id
        )
        new_payment.payment_url = new_url
        new_payment.yookassa_id = yookassa_id
    except Exception:
        raise HTTPException(503, detail="Payment provider error")

    await db.commit()

    return new_url
