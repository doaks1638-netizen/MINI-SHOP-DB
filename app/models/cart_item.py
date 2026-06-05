from app.models import Base, idpk
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint, PrimaryKeyConstraint
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User, Product


class CartItem(Base):
    __tablename__ = "carts"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    amount: Mapped[int]

    user: Mapped["User"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship(back_populates="cart_items")

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "product_id"),
        CheckConstraint("amount > 0", name="cart_item_amount_positive"),
    )
