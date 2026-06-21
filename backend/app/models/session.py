from app.models.base import Base, idpk, active
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime
from uuid import UUID
from sqlalchemy import ForeignKey
from datetime import datetime
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.user import User


class UserSession(Base):
    __tablename__ = "sessions"

    id: Mapped[idpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    active_token_id: Mapped[UUID]
    is_active: Mapped[active]
    expiration_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()
