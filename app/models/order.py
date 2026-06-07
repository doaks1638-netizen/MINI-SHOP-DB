from app.models import Base, idpk, OrderStatus
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, text
from sqlalchemy.types import Enum, Numeric
from datetime import datetime
from uuid6 import UUID as UUID7
from typing import TYPE_CHECKING
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.order_item import OrderItem


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[idpk]
    user_id: Mapped[UUID7] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    status: Mapped["OrderStatus"] = mapped_column(
        Enum(OrderStatus, native_enum=False), default=OrderStatus.created
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
