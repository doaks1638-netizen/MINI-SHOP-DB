from app.models import Base, idpk, active
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, Numeric
from sqlalchemy import text, CheckConstraint
from decimal import Decimal


class User(Base):
    __tablename__ = "users"

    id: Mapped[idpk]
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    hash_password: Mapped[str] = mapped_column(String(100))
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default=text("0"))
    is_active: Mapped[active]

    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_user_balance_positive"),
    )
