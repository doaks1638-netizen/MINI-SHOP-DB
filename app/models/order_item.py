from app.models import Base
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, CheckConstraint
from sqlalchemy.types import Numeric
from uuid import UUID


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT")
    )
    amount: Mapped[int]
    price_for_one: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    __table_args__ = (
        PrimaryKeyConstraint("order_id", "product_id"),
        CheckConstraint("amount > 0", name="check_amount_positive"),
        CheckConstraint("price_for_one >= 0", name="check_price_positive"),
    )
