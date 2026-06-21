from yookassa import Configuration, Payment
from decimal import Decimal
from app.settings import settings
from anyio import to_thread
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from fastapi import HTTPException
from uuid import UUID


async def create_yookaassa_payment(db: AsyncSession, amount: Decimal, idempotency_key):

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    payment = {
        "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": settings.YOOKASSA_RETURN_URL,
        },
        "capture": True,
        "description": "Пополнение баланса пользователя",
    }

    def _request(payment: dict, idempotency_key: str) -> Payment:
        return Payment.create(payment, str(idempotency_key))

    payment: Payment = await to_thread.run_sync(_request, payment, idempotency_key)

    confirmation_url = getattr(payment.confirmation, "confirmation_url", None)

    return (payment.id, confirmation_url)


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
