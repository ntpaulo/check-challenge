from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.config.db import SessionLocal
from app.modules.auth.auth_dto import RegisterRequestDTO
from app.modules.auth.auth_service import login_user, register_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    try:
        return login_user(db, form_data.username, form_data.password)
    finally:
        db.close()


@router.post("/register")
def register(data: RegisterRequestDTO):
    db = SessionLocal()
    try:
        return register_user(db, data.name, data.email, data.password)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
