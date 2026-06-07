# schemes placed in a separate file to avoid circular imports

from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from uuid6 import UUID
from typing import Annotated
from datetime import datetime
from app.models import OrderStatus


class CartItemShare(BaseModel):
    user_id: UUID
    product_id: UUID
    amount: Annotated[int, Field(gt=0)]
    model_config = ConfigDict(from_attributes=True)


class CategoryShare(BaseModel):
    id: UUID
    name: Annotated[str, Field(max_length=50)]
    model_config = ConfigDict(from_attributes=True)


class OrderShare(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    status: OrderStatus
    model_config = ConfigDict(from_attributes=True)


class ProductShare(BaseModel):
    id: UUID
    category_id: UUID
    name: Annotated[str, Field(max_length=100)]
    price: Annotated[Decimal, Field(ge=0)]
    now_amount: Annotated[int, Field(ge=0)]
    model_config = ConfigDict(from_attributes=True)


class UserShare(BaseModel):
    id: UUID
    name: Annotated[str, Field(max_length=100)]
    balance: Annotated[Decimal, Field(ge=0)]
    model_config = ConfigDict(from_attributes=True)
