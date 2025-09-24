from enum import Enum as PyEnum
from .database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, Integer, String, Boolean, Date, TIMESTAMP, ForeignKey, DateTime,Enum, Time, ARRAY, Float, Text

class UserRole(str, PyEnum):
    ADMIN = "admin"
    AUTHOR = "author"
    REVIEWER = "reviewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(225), index=True)
    hashed_password = Column(String(225))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ADMIN)