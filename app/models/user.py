from app.models import Base, idpk
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Numeric
from sqlalchemy import text, CheckConstraint
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.order import Order


class User(Base):
    __tablename__ = "users"

    id: Mapped[idpk]
    name: Mapped[str] = mapped_column(String(100))
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default=text("0"))

    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_user_balance_positive"),
    )
