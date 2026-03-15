from fastapi import HTTPException

from app.db.models import CheckIn, User


def create_user_checkin(db, current_user):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    checkin = CheckIn(user_id=current_user.id)

    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return {
        "id": checkin.id,
        "user_name": user.name,
        "user_id": checkin.user_id,
        "created_at": checkin.created_at,
    }


def list_all_chekins(db, current_user):
    return db.query(CheckIn).all()
