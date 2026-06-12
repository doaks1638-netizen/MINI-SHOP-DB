from app.models import Base, idpk, active
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, Numeric, Enum
from sqlalchemy import text, CheckConstraint, UniqueConstraint
from decimal import Decimal
from app.models import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[idpk]
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    hash_password: Mapped[str]
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default=text("0"))
    is_active: Mapped[active]
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False), default=UserRole.user
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_user_balance_positive"),
        UniqueConstraint("email"),
    )
