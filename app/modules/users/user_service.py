from app.db.models import User


def list_all_users(db, current_user):
    return db.query(User).all()
