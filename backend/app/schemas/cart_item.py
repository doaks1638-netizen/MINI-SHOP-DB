from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Annotated
from enum import Enum
from app.models.enums import UserStatus


class CartItemStatus(str, Enum):
    out_of_stock = "out_of_stock"
    in_stock = "in_stock"


class Cart(
    BaseModel
):  # replaces the one-to-one relationship with the user's cart (combining all items into one cart)
    user_id: UUID
    total_products: int
    total_items: int


class AdminCart(Cart):
    user_status: UserStatus


class CartItemDTO(BaseModel):
    product_id: UUID
    amount: Annotated[int, Field(gt=0)]
    model_config = ConfigDict(from_attributes=True)


class AdminCartItemDTO(CartItemDTO):
    user_status: UserStatus


class CartItemWithStatus(CartItemDTO):
    status: CartItemStatus
