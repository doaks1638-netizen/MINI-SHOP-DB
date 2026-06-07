from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from uuid import UUID
from decimal import Decimal
from app.schemas.shared import CartItemShare, CategoryShare


class ProductCreate(BaseModel):
    category_id: UUID
    name: Annotated[str, Field(max_length=100)]
    price: Annotated[Decimal, Field(ge=0)]
    now_amount: Annotated[int, Field(ge=0)]


class ProductDTO(ProductCreate):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class ProductRelDTO(ProductDTO):
    cart_items: list[CartItemShare] = []
    category: CategoryShare
