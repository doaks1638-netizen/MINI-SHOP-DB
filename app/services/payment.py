from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from decimal import Decimal
from fastapi import HTTPException


async def debit_funds(db: AsyncSession, user_id: UUID, diff: Decimal):
    stmt = (
        select(User)
        .where(User.id == user_id)
        .where(User.is_active == True)
        .with_for_update()
    )
    user = await db.scalar(stmt)
    if not user:
        raise HTTPException(status_code=404, detail="User not found or inactive")
    new_balance = user.balance + diff
    if new_balance < 0:
        raise HTTPException(status_code=402, detail="Insufficient funds in the account")
    user.balance = new_balance
