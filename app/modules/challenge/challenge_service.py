from app.db.models import Challenge, User


def create_challenge_for_user(db, challenge, current_user):
    user = db.query(User).filter(User.id == current_user.id).first()

    challenge = Challenge(
        title=challenge.title,
        duration=challenge.duration,
        start_date=challenge.start_date,
    )
    challenge.users.append(user)
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return {
        "id": challenge.id,
        "title": challenge.title,
        "duration": challenge.duration,
        "start_date": challenge.start_date,
    }


def list_challenges(db, current_user):
    user = db.query(User).filter(User.id == current_user.id).first()
    challenge = []

    for c in user.challenge:
        challenge.append(
            {
                "id": c.id,
                "title": c.title,
                "duration": c.duration,
                "start_date": c.start_date,
                "users": [{"id": u.id, "name": u.name} for u in c.users],
            }
        )

    return challenge


def add_user_to_challenge(db, challenge_id: int, user_id: int):
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise ValueError("Challenge nao existe")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User nao existe")
    
    if user in challenge.users:
        return {
            "id": challenge.id,
            "title": challenge.title,
            "users": [{"id": u.id, "name": u.name} for u in challenge.users],
            "message": "User ja esta no desafio",
        }

    challenge.users.append(user)
    db.commit()
    db.refresh(challenge)

    return {
        "id": challenge.id,
        "title": challenge.title,
        "users": [{"id": u.id, "name": u.name} for u in challenge.users],
    }

