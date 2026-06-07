from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated
from uuid6 import uuid7
from uuid import UUID
from sqlalchemy import text, UUID as UUID_sql


class Base(DeclarativeBase):
    pass

idpk = Annotated[
    UUID, mapped_column(primary_key=True,default=uuid7, server_default=text('uuidv7()'))
]
