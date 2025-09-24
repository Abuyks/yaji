from sqlalchemy.orm import Session,joinedload
from sqlalchemy.sql import case
from sqlalchemy import or_, desc, asc
from datetime import datetime, timezone, timedelta
from . import models, schemas, utils
from .auth import get_password_hash, get_current_user
#from .models import Role, WithdrawalStatus
from fastapi import HTTPException,UploadFile, Depends
import asyncio
#import pytz
from typing import Optional
from secrets import token_urlsafe
from uuid import uuid4
import random

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user