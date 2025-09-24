from pydantic import (
    BaseModel,
    EmailStr,
    constr,Field,
    field_validator,
    StringConstraints,
    PastDate, ConfigDict
)
from enum import Enum
from typing_extensions import Annotated
from typing import Optional, List,Literal
from datetime import date, datetime,time as eventtime
import re

ALLOWED_USERNAME_REGEX = r"^[a-zA-Z0-9_]+$"

class UserRole(str, Enum):
    ADMIN = "admin"
    AUTHOR = "author"
    REVIEWER = "reviewer"

class UserBase(BaseModel):
    email: Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)
    ]
    role: UserRole  # 👈 Add role

class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=1, max_length=100)]

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: Optional[str] = None
    role: UserRole


    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole 
    email: str

class TokenData(BaseModel):
    email: str | None = None