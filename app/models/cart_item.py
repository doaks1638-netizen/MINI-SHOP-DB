from app.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint, PrimaryKeyConstraint
from uuid6 import UUID as UUID7
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class CartItem(Base):
    __tablename__ = "carts"

    user_id: Mapped[UUID7] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[UUID7] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    amount: Mapped[int]

    user: Mapped["User"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship(back_populates="cart_items")

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "product_id", name="cart_user_product_pk"),
        CheckConstraint("amount > 0", name="cart_item_amount_positive"),
    )
