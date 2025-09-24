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
    prefix= "/api/authors",
    tags=["Authors Module"]
)

@router.post("/papers", response_model=schemas.PaperResponse)
async def upload_paper(
    title: str,
    abstract: str,
    keywords: str = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.AUTHOR:
        raise HTTPException(status_code=403, detail="Only authors can upload papers")

    # Save file locally (you can replace with S3, etc.)
    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    paper_data = schemas.PaperCreate(title=title, abstract=abstract, keywords=keywords)
    return crud.create_paper(db=db, paper=paper_data, file_path=file_location, author_id=current_user.id)


# 📌 Get all submitted papers
@router.get("/papers", response_model=List[schemas.PaperResponse])
async def get_my_papers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.AUTHOR:
        raise HTTPException(status_code=403, detail="Only authors can view their papers")

    return crud.get_papers_by_author(db=db, author_id=current_user.id)