from app.models import Base, idpk
from sqlalchemy.types import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[idpk]
    name: Mapped[str] = mapped_column(String(50), unique=True)

    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
        single_parent=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
