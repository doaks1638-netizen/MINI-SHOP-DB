from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from app.schemas.shared import UserShare, ProductShare
from typing import Annotated


class CartItemDTO(BaseModel):
    user_id: UUID
    product_id: UUID
    amount: Annotated[int, Field(gt=0)]
    model_config = ConfigDict(from_attributes=True)


class CartItemRelDTO(CartItemDTO):
    user: UserShare
    product: ProductShare
