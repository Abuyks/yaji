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

def create_paper(db: Session, paper: schemas.PaperCreate, file_path: str, author_id: int):
    db_paper = models.Paper(
        title=paper.title,
        abstract=paper.abstract,
        keywords=paper.keywords,
        file_path=file_path,
        author_id=author_id,
        status=models.PaperStatus.PENDING,
        version=1,
        uploaded_at=datetime.utcnow(),
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper

def get_all_papers(db: Session):
    return (
        db.query(models.Paper)
        .options(joinedload(models.Paper.author))
        .all()
    )

def get_all_reviewers(db: Session):
    return db.query(models.User).filter(models.User.role == models.UserRole.REVIEWER).all()



def get_papers_by_author(db: Session, author_id: int):
    return db.query(models.Paper).filter(models.Paper.author_id == author_id).all()

def assign_reviewer(db: Session, paper_id: int, reviewer_id: int):
    assignment = models.Assignment(paper_id=paper_id, reviewer_id=reviewer_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def remove_reviewer(db: Session, paper_id: int, reviewer_id: int):
    assignment = (
        db.query(models.Assignment)
        .filter(
            models.Assignment.paper_id == paper_id,
            models.Assignment.reviewer_id == reviewer_id,
        )
        .first()
    )
    if assignment:
        db.delete(assignment)
        db.commit()
    return assignment


def get_all_assigned_papers(db: Session):
    return (
        db.query(models.Assignment)
        .options(joinedload(models.Assignment.paper), joinedload(models.Assignment.reviewer))
        .all()
    )


# ---------- Reviewer ----------
def get_reviewer_papers(db: Session, reviewer_id: int):
    return (
        db.query(models.Assignment)
        .filter(models.Assignment.reviewer_id == reviewer_id)
        .options(
            joinedload(models.Assignment.paper).joinedload(models.Paper.author),
            joinedload(models.Assignment.reviewer),
        )
        .all()
    )



def update_paper_status(db: Session, paper_id: int, status: models.PaperStatus):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if paper:
        paper.status = status
        db.commit()
        db.refresh(paper)
    return paper

from sqlalchemy import func

def get_all_reviewers_with_counts(db: Session):
    return (
        db.query(
            models.User.id,
            models.User.email,
            models.User.role,
            func.count(models.Assignment.id).label("assigned_papers_count"),
        )
        .outerjoin(models.Assignment, models.Assignment.reviewer_id == models.User.id)
        .filter(models.User.role == models.UserRole.REVIEWER)
        .group_by(models.User.id)
        .all()
    )
