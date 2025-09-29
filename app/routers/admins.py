from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Form, APIRouter, UploadFile,File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from .. import models, schemas, crud, auth, utils
from sqlalchemy.orm import Session
from .. database import engine, SessionLocal, get_db
from datetime import timedelta
from typing import List
import jwt
from ..auth import get_current_user 
import shutil
import os

router = APIRouter(
    prefix= "/api/admins",
    tags=["Admins Module"]
)


@router.get("/papers", response_model=List[schemas.PaperResponse])
def get_all_papers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view all papers")

    papers = crud.get_all_papers(db)

    base_url = "http://127.0.0.1:8000"  # or use request.base_url if you prefer
    return [
        schemas.PaperResponse(
            id=p.id,
            title=p.title,
            abstract=p.abstract,
            keywords=p.keywords,
            status=p.status,
            version=p.version,
            uploaded_at=p.uploaded_at,
            author=p.author,
            file_url=f"{base_url}/uploads/{os.path.basename(p.file_path)}" if p.file_path else None,
            reviewer_comment=p.reviewer_comment,
        )
        for p in papers
    ]

 # ✅ Pydantic will handle `author` via ORM because of from_attributes


@router.get("/reviewers", response_model=List[schemas.ReviewerWithCountResponse])
def get_all_reviewers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can access reviewers")

    reviewers = crud.get_all_reviewers_with_counts(db)

    # Convert row objects to dict for schema
    return [
        schemas.ReviewerWithCountResponse(
            id=r.id,
            email=r.email,
            role=r.role,
            assigned_papers_count=r.assigned_papers_count,
        )
        for r in reviewers
    ]




@router.post("/assign", response_model=schemas.AssignmentResponse)
def assign_paper(
    assignment: schemas.AssignmentBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can assign reviewers")

    db_assignment = crud.assign_reviewer(db, paper_id=assignment.paper_id, reviewer_id=assignment.reviewer_id)

    return db_assignment


@router.delete("/remove", response_model=schemas.AssignmentResponse)
def remove_paper(
    assignment: schemas.AssignmentBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can remove assignments")

    removed = crud.remove_reviewer(db, paper_id=assignment.paper_id, reviewer_id=assignment.reviewer_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return removed


@router.get("/assigned", response_model=List[schemas.AssignmentResponse])
def get_all_assigned(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view all assignments")

    assignments = crud.get_all_assigned_papers(db)

    return [
        schemas.AssignmentResponse(
            id=a.id,
            paper_id=a.paper_id,
            reviewer_id=a.reviewer_id,
            assigned_date=a.assigned_date,
            title=a.paper.title,
            author_name=a.paper.author.email,
            reviewer_name=a.reviewer.email,
            status=a.paper.status.value,
        )
        for a in assignments
    ]