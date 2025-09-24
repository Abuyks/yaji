from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
# from . import models, schemas, crud, auth, utils
from .database import engine, SessionLocal, Base
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
from .routers import users


app = FastAPI(
    title = "Yaji",
    #docs_url=None,  # Disable Swagger UI
    #redoc_url=None, # Disable ReDoc UI
)

Base.metadata.create_all(bind=engine)

origins = [
  "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
