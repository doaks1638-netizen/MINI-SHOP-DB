from app.models import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint, PrimaryKeyConstraint
from uuid import UUID


class CartItem(Base):
    __tablename__ = "carts"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    amount: Mapped[int]

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "product_id", name="cart_user_product_pk"),
        CheckConstraint("amount > 0", name="cart_item_amount_positive"),
    )
