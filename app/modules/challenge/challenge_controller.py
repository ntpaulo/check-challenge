from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models import User
from app.modules.challenge.challenge_dto import ChallengeRequestDTO
from app.modules.challenge.challenge_service import (
    add_user_to_challenge,
    create_challenge_for_user,
    list_challenges,
)
from app.shared.dependecies.auth_dependency import get_current_user
from app.shared.dependecies.db_dependency import get_db


router = APIRouter(prefix="/challenges", tags=["check-challenge"])


@router.post("/")
def create_challenge(
    challenge: ChallengeRequestDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return create_challenge_for_user(db, challenge, current_user)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.get("/")
def list_user_challenges(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    try:
        return list_challenges(db, current_user)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@router.post("/{challenge_id}/join/{user_id}")
def join_user_to_challenge(challenge_id: int, user_id: int, db: Session = Depends(get_db)):
    try:
        return add_user_to_challenge(db, challenge_id, user_id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close