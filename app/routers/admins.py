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


@router.post("/assign", response_model=schemas.AssignmentResponse)
def assign_paper(
    assignment: schemas.AssignmentBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can assign reviewers")

    db_assignment = crud.assign_reviewer(db, paper_id=assignment.paper_id, reviewer_id=assignment.reviewer_id)

    return schemas.AssignmentResponse(
        id=db_assignment.id,
        paper_id=db_assignment.paper_id,
        reviewer_id=db_assignment.reviewer_id,
        assigned_date=db_assignment.assigned_date,
        title=db_assignment.paper.title,
        author_name=db_assignment.paper.author.email,
        reviewer_name=db_assignment.reviewer.email,
        status=db_assignment.paper.status.value,
    )


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