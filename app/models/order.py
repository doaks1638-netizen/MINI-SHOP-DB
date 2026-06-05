from app.models import Base, idpk
from app.models import OrderStatus
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, text
from sqlalchemy.types import Enum
from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[idpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    status: Mapped["OrderStatus"] = mapped_column(
        Enum(OrderStatus, native_enum=False), default=OrderStatus.created
    )

    user: Mapped["User"] = relationship(back_populates="orders")
