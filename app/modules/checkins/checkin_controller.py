from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.db import SessionLocal
from app.db.models import CheckIn, User
from app.modules.checkins.checkin_service import list_all_chekins, create_user_checkin
from app.shared.dependecies.auth_dependency import get_current_user
from app.shared.dependecies.db_dependency import get_db


router = APIRouter(prefix="/checkins", tags=["check-challenge"])


@router.get("/list_checkins")
def list_checkins(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    try:
        return list_all_chekins(db, current_user)
    finally:
        db.close()


@router.post("/")
def create_checkins(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        return create_user_checkin(db, current_user)
    finally:
        db.close()
