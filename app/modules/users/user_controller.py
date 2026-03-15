from app.modules.users.user_service import list_all_users
from app.shared.dependecies.auth_dependency import get_current_user
from app.shared.dependecies.db_dependency import get_db
from app.db.models import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


router = APIRouter(prefix="/user", tags=["check-challenge"])


@router.get("/list_users")
def list_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    try:
        return list_all_users(db, current_user)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.get("/me")
def read_me(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):

    try:
        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        }
    except Exception():
        db.rollback()
        raise
    finally:
        db.close()
