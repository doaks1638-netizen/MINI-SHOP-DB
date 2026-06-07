from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Annotated


class Cart(
    BaseModel
):  # replaces the one-to-one relationship with the user's cart (combining all items into one cart)
    user_id: UUID
    total_products: int
    total_items: int


class CartItemView(
    BaseModel
):  # this model show of items in user cart - for beautiful view
    product_id: UUID
    amount: Annotated[int, Field(gt=0)]
    model_config = ConfigDict(from_attributes=True)


class CartItemDTO(CartItemView):  # data transfer object for new item creation
    user_id: UUID
