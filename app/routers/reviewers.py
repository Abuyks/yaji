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
    prefix= "/api/reviewers",
    tags=["Reviewers Module"]
)

@router.get("/papers", response_model=List[schemas.AssignmentResponse])
def get_my_assigned_papers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.REVIEWER:
        raise HTTPException(status_code=403, detail="Only reviewers can access assigned papers")

    assignments = crud.get_reviewer_papers(db, reviewer_id=current_user.id)

    base_url = "http://127.0.0.1:8000"
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
            file_url=f"{base_url}/uploads/{os.path.basename(a.paper.file_path)}" if a.paper.file_path else None,
        )
        for a in assignments
    ]


@router.patch("/papers/{paper_id}/status", response_model=schemas.PaperResponse)
def update_status(
    paper_id: int,
    update: schemas.PaperStatusUpdate,   # 👈 use new schema
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.REVIEWER:
        raise HTTPException(status_code=403, detail="Only reviewers can update paper status")

    paper = crud.update_paper_status(
        db, 
        paper_id=paper_id, 
        status=update.status, 
        reviewer_comment=update.reviewer_comment  # 👈 save reason
    )
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return paper
