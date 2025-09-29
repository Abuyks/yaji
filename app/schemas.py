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

class PaperStatus(str, Enum):
    pending = "pending"
    accept = "accept"
    reject = "reject"
    revise = "revise"


class PaperBase(BaseModel):
    title: str
    abstract: str
    keywords: Optional[str] = None


class PaperCreate(PaperBase):
    pass   # file will be handled separately


# class PaperResponse(PaperBase):
#     id: int
#     status: PaperStatus
#     version: int
#     uploaded_at: datetime
#     author: UserResponse

#     class Config:
#         from_attributes = True

class PaperResponse(PaperBase):
    id: int
    status: PaperStatus
    version: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    author: Optional[UserResponse] = None
    file_url: Optional[str] = None  # ✅ add this
    reviewer_comment: Optional[str] = None

    class Config:
        from_attributes = True

class PaperStatusUpdate(BaseModel):
    status: PaperStatus
    reviewer_comment: Optional[str] = None   # ✅ reviewer can leave reason



class AssignmentBase(BaseModel):
    paper_id: int
    reviewer_id: int


class AssignmentResponse(BaseModel):
    id: int
    assigned_date: datetime
    paper: PaperResponse       # 👈 nested paper info
    reviewer: UserResponse     # 👈 nested reviewer info

    class Config:
        from_attributes = True

class ReviewerWithCountResponse(BaseModel):
    id: int
    email: str
    role: str
    assigned_papers_count: int

    class Config:
        from_attributes = True
