from app.models.base import Base, idpk
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String
from sqlalchemy import ForeignKey
from uuid import UUID
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class EmailCode(Base):
    __tablename__ = "email_codes"

    id: Mapped[idpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expire_at: Mapped[datetime]
    code: Mapped[str] = mapped_column(String(6))

    user: Mapped["User"] = relationship()


class EmailUrl(Base):
    __tablename__ = "email_urls"

    id: Mapped[idpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expire_at: Mapped[datetime]
    token: Mapped[UUID]
    # I separate the token ID and id because I use UUID4 for the token and UUID6 for the database.

    user: Mapped["User"] = relationship()
