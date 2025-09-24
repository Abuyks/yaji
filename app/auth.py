from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from . import models, schemas, crud, utils
from .database import SessionLocal
from .config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login_user")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, identifier: str, password: str):
    """Authenticate user by email or phone number only."""
    
    # Check if user exists by email
    user_by_email = db.query(models.User).filter(models.User.email == identifier).first()
    if user_by_email and utils.verify_password(password, user_by_email.hashed_password):
        return user_by_email, "email"

    # Check if user exists by phone number
    user_by_phone = db.query(models.User).filter(models.User.phone == identifier).first()
    if user_by_phone and utils.verify_password(password, user_by_phone.hashed_password):
        return user_by_phone, "phone"

    return None, None  # User not found



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
   
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """Retrieve the current user using email (since username is removed)."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # We now store email instead of username
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)  # Use email instead of username
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=token_data.email)  # Fetch by email
    if user is None:
        raise credentials_exception

    return user


def get_current_user_invite(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    if token is None:
        # No token is provided, treat as an unauthenticated user
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Fetch user from the database
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=400, detail="Not found")
    return current_user

# #Album Module

# def create_album(db: Session, album: schemas.AlbumCreate, user_id: int):
#     db_album = models.Album(**album.model_dump(), user_id=user_id)
#     db.add(db_album)
#     db.commit()
#     db.refresh(db_album)
#     return db_album

# def get_albums(db: Session, user_id: int):
#     return db.query(models.Album).filter(models.Album.user_id == user_id).all()

# def get_album(db: Session, album_id: int, user_id: int):
#     return db.query(models.Album).filter(models.Album.id == album_id, models.Album.user_id == user_id).first()

# def update_album(db: Session, album_id: int, album: schemas.AlbumCreate, user_id: int):
#     db_album = get_album(db, album_id, user_id)
#     if db_album:
#         db_album.title = album.title
#         db_album.image = album.image
#         db.commit()
#         db.refresh(db_album)
#     return db_album

# def delete_album(db: Session, album_id: int, user_id: int):
#     db_album = get_album(db, album_id, user_id)
#     if db_album:
#         db.delete(db_album)
#         db.commit()
#     return db_album

def super_admin_required(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Only super admins allowed")
    return current_user