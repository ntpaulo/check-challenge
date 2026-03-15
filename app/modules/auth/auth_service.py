from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config.db import SessionLocal
from app.config.security import create_acess_token, hash_password, verify_password
from app.db.models import User
from app.modules.auth.auth_dto import RegisterRequestDTO


def login_user(db: Session, email: str, password: str):

    # Busca usuário no banco
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    # verifica a senha
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    # gera token
    token = create_acess_token({"sub": str(user.id)})

    return {"access_token": token, "type_token": "bearer"}


def register_user(db: Session, name: str, email: str, password: str):
    existing = db.query(User).filter(User.email == email).first()
    # 1) Verifica se já existe usuário com esse email
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # 2) Cria o usuário com senha hasheada
    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
    )

    # 3) Salva no banco
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "name": user.name, "email": user.email}
