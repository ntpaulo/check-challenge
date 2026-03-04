from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from app.db.models import User, Challenge, CheckIn
from app.db.session import SessionLocal, engine, Base

app = FastAPI()

load_dotenv()

# Auth (hash de senha)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    # gera hash seguro (argon2)
    return pwd_context.hash(password)


# verifica se a senha informada é a mesma da senha hash no banco
def verify_password(plain_password: str, hash_password: str) -> bool:
    return pwd_context.verify(plain_password, hash_password)


def create_acess_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return user
    finally:
        db.close()


@app.get("/users/me", tags=["Auth"])
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }


@app.post("/auth/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    try:
        # Busca usuário no banco
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Email ou senha inválidos")
        # verifica a senha
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Email ou senha inválidos")

        # gera token
        token = create_acess_token({"sub": str(user.id)})

        return {"access_token": token, "type_token": "bearer"}
    finally:
        db.close()


@app.post("/auth/register", tags=["Auth"])
def register(data: RegisterRequest):
    db = SessionLocal()
    try:
        # 1) Verifica se já existe usuário com esse email
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        # 2) Cria o usuário com senha hasheada
        user = User(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )

        # 3) Salva no banco
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"id": user.id, "name": user.name, "email": user.email}
    except Exception:
        db.rollback
        raise
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse, tags=["check-challenge"])
def root():
    return """
    <html>
        <head>
            <title> CheckChallenge </title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    color: #333;
                    text-align: center;
                    padding: 50px;
                }
                h1 {
                    color: #007BFF;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    background-color: #fff;
                    margin: 10px auto;
                    padding: 10px;
                    width: 200px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background-color: #007BFF;
                    color: #fff;
                    text-decoration: none;
                    border-radius: 5px;
                }
                a:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <h1>🚀📆 Check Challenge API</h1>
            <p>API rodando com sucesso!</p>
            <ul>
                <li>POST /users</li>
                <li>GET /users</li>
                <li>POST /challenge</li>
                <li>GET /challenges</li>
                <li>POST /checkin</li>
            </ul>
            <a href="/docs">🚀 Acessar Swagger</a>
        </body>
    </html>
    """


@app.get("/users", tags=["check-challenge"])
def list_users(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()


class ChallengeRequest(BaseModel):
    title: str
    duration: int
    start_date: str


@app.post("/challenge", tags=["check-challenge"])
def create_challenge(
    challenge: ChallengeRequest,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
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

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@app.get("/challenges", tags=["check-challenge"])
def list_challenges(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user.id).first()

        challenges = []

        for c in user.challenge:
            challenges.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "duration": c.duration,
                    "start_date": c.start_date,
                    "users": [{"id": u.id, "name": u.name} for u in c.users],
                }
            )

        return challenges
    finally:
        db.close


@app.post("/checkin", tags=["check-challenge"])
def create_checkin(user_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        checkin = CheckIn(user_id=user_id)
        db.add(checkin)
        db.commit()
        db.refresh(checkin)
        return {
            "id": checkin.id,
            "user_name": user.name,
            "user_id": checkin.user_id,
            "created_at": checkin.created_at,
        }
    finally:
        db.close()


@app.get("/checkins", tags=["check-challenge"])
def list_checkins(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        checkins = db.query(CheckIn).all()
        return checkins
    finally:
        db.close()
