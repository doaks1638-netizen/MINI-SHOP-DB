from app.models.base import Base, idpk
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from app.models.enums import PaymentStatus
from app.models import User
from sqlalchemy.types import DateTime
from fastapi import HTTPException


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[idpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[Decimal] = mapped_column()
    yookassa_id: Mapped[str | None] = mapped_column(default=None)
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.pending)
    payment_url: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
