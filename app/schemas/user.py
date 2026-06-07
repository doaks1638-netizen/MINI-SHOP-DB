from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Annotated
from uuid import UUID


class UserCreate(BaseModel):  # auntification on future
    name: Annotated[str, Field(max_length=100)]


class UserDTO(UserCreate):
    id: UUID
    balance: Annotated[Decimal, Field(ge=0)]
    model_config = ConfigDict(from_attributes=True)


class UserRelCount(UserDTO):
    orders_count: Annotated[int, Field(ge=0)]


class UserPatch(BaseModel):
    name: Annotated[str, Field(max_length=100)]
