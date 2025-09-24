from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Form, APIRouter, UploadFile,File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from .. import models, schemas, crud, auth, utils
from sqlalchemy.orm import Session
from .. database import engine, SessionLocal, get_db
from datetime import timedelta
from typing import List
import jwt


router = APIRouter(
    prefix= "/api/users",
    tags=["Users Module"]
)

# @router.post("/", response_model=schemas.UserResponse)
# def create_user(
#     user_data: schemas.UserCreate,
#     db: Session = Depends(get_db),
#     current_user: schemas.User = Depends(auth.get_current_active_user)
# ):
#     return crud.create_user(db, user_data, user_id=current_user.id)

@router.post(
    "/create_user/",
    response_model=schemas.User,
    description="Create a new user account",
)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    user.email = user.email.lower()

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user.role not in schemas.UserRole:
        raise HTTPException(status_code=400, detail="Invalid role")


    new_user = crud.create_user(db=db, user=user)

    return new_user



def identify_type(identifier: str) -> str:
    """Identify whether the input is an email or phone number."""
    if "@" in identifier:
        return "email"
    else:
        return None  # Username is not allowed



@router.post(
    "/login_user",
    response_model=schemas.Token,
    description="Login using email",
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    identifier_type = identify_type(form_data.username)

    if not identifier_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid login. Use email or phone number.",
        )

    identifier = form_data.username.lower() if identifier_type == "email" else form_data.username

    # Fetch user based on email or phone
    if identifier_type == "email":
        user = crud.get_user_by_email(db, email=identifier)

    # Validate user credentials
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


    access_token = auth.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer", "role": user.role,"email" : user.email}