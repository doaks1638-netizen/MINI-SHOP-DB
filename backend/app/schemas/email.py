from pydantic import BaseModel
from pydantic import EmailStr

class EmailSchema(BaseModel):
    email: EmailStr
