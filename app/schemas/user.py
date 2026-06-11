from pydantic import BaseModel, ConfigDict, Field, EmailStr
from decimal import Decimal
from typing import Annotated
from uuid import UUID
from app.models.user_role_enum import UserRole


class UserCreate(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class UserDTO(BaseModel):
    id: UUID
    name: Annotated[str, Field(max_length=100)]
    email: EmailStr
    balance: Annotated[Decimal, Field(ge=0)]
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserRelCount(UserDTO):
    orders_count: Annotated[int, Field(ge=0)]


class UserPatch(BaseModel):
    name: Annotated[str, Field(max_length=100)]


class UserPatchRole(BaseModel):
    role: UserRole
