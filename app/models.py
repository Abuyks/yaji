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

from datetime import datetime



class PaperStatus(str, PyEnum):
    PENDING = "pending"
    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    abstract = Column(Text, nullable=False)
    keywords = Column(String(255))
    file_path = Column(String(255), nullable=False)   # path to uploaded file
    status = Column(Enum(PaperStatus), default=PaperStatus.PENDING, nullable=False)
    version = Column(Integer, default=1)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    reviewer_comment = Column(Text, nullable=True) 

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", backref="papers")

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    assigned_date = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", backref="assignments")
    reviewer = relationship("User", backref="assigned_papers")

