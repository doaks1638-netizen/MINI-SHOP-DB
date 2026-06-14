from app.models.base import Base, idpk, active
from sqlalchemy.types import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint, Computed, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from uuid import UUID
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.categories import Category


class Product(Base):
    __tablename__ = "products"

    id: Mapped[idpk]
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    now_amount: Mapped[int]
    is_active: Mapped[active]
    image_url: Mapped[str | None] = None

    category: Mapped["Category"] = relationship(back_populates="products")

    tsv: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            """
        setweight(to_tsvector('english', coalesce(name, '')), 'A')
        ||
        setweight(to_tsvector('russian', coalesce(name, '')), 'A')
        ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B')
        ||
        setweight(to_tsvector('russian', coalesce(description, '')), 'B')
        """,
            persisted=True,
        ),
    )

    __table_args__ = (
        CheckConstraint("now_amount >= 0", name="product_amount_positive"),
        CheckConstraint("price >= 0", name="product_price_positive"),
        UniqueConstraint("category_id", "name"),
        Index("ix_products_tsv_gin", "tsv", postgresql_using="gin"),
    )
