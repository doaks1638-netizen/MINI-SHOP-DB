from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from uuid import UUID
from decimal import Decimal
from app.schemas.categories import CategoryDTO


class ProductCreate(BaseModel):
    category_id: UUID
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str | None, Field(max_length=200)] = None
    price: Annotated[Decimal, Field(ge=0)]
    now_amount: Annotated[int, Field(ge=0)]
    is_active: bool


class ProductDTO(ProductCreate):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class ProductRelDTO(ProductDTO):
    category: CategoryDTO


class ProductPatch(BaseModel):
    category_id: UUID | None = None
    name: Annotated[str | None, Field(max_length=100)] = None
    description: Annotated[str | None, Field(max_length=200)] = None
    price: Annotated[Decimal | None, Field(ge=0)] = None
    now_amount: Annotated[int | None, Field(ge=0)] = None
    is_active: bool = True
