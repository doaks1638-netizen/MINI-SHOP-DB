from app.models import Base, idpk, OrderStatus
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, text
from sqlalchemy.types import Enum, Numeric, DateTime
from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.product import Product


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[idpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
    status: Mapped["OrderStatus"] = mapped_column(
        Enum(OrderStatus, native_enum=False),
        default=OrderStatus.created,
        server_default="created",
    )
    price_for_one: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), server_default=text("0")
    )
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    amount: Mapped[int]

    product: Mapped['Product'] = relationship()
