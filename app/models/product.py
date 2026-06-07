from app.models import Base, idpk
from sqlalchemy.types import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint
from uuid6 import UUID as UUID7
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.categories import Category
    from app.models.order_item import OrderItem


class Product(Base):
    __tablename__ = "products"

    id: Mapped[idpk]
    category_id: Mapped[UUID7] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    now_amount: Mapped[int]

    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    category: Mapped["Category"] = relationship(back_populates="products")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="product")

    __table_args__ = (
        CheckConstraint("now_amount >= 0", name="product_amount_positive"),
        CheckConstraint("price >= 0", name="product_price_positive"),
    )
