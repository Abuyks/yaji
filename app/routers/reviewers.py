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

    return crud.get_reviewer_papers(db, reviewer_id=current_user.id)


@router.patch("/papers/{paper_id}/status", response_model=schemas.PaperResponse)
def update_status(
    paper_id: int,
    status: schemas.PaperStatus,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.REVIEWER:
        raise HTTPException(status_code=403, detail="Only reviewers can update paper status")

    paper = crud.update_paper_status(db, paper_id=paper_id, status=status)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return paper