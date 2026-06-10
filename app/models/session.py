from app.models import Base, idpk, active
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    expiration_time: Mapped[datetime]

    user: Mapped["User"] = relationship()
