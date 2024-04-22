from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    surname: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(default=None)
    phone: Optional[str] = Field(default=None)
    date_of_birth: Optional[date] = Field(default=None)


class ContactSchemaResponse(ContactSchema):
    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=3)

    class Config:
        from_attributes = True


class UserSchema(UserLoginSchema):
    username: str = Field(min_length=3, max_length=50)

    class Config:
        from_attributes = True
