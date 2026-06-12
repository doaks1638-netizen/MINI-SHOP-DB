from pydantic import BaseModel, ConfigDict, Field, EmailStr
from decimal import Decimal
from typing import Annotated
from uuid import UUID
from app.models import UserRole, CreatorUserRole


class UserCreate(BaseModel):
    google_id: str
    name: Annotated[str, Field(max_length=256)]
    email: EmailStr
    picture: str


class UserDTO(BaseModel):
    id: UUID
    name: Annotated[str, Field(max_length=100)]
    email: EmailStr
    balance: Annotated[Decimal, Field(ge=0)]
    role: UserRole
    picture: str
    model_config = ConfigDict(from_attributes=True)


class UserDTOCount(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    orders_count: Annotated[int, Field(ge=0)]


class UserPatch(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    picture: str


class UserPatchRole(BaseModel):
    role: CreatorUserRole


class BalanceUpdate(BaseModel):
    update_amount: Annotated[Decimal, Field(ge=0, le=10000000)]


class NewBalance(BaseModel):
    balance: Decimal
