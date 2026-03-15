from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.config.db import engine, Base

from app.modules.auth.auth_controller import router as auth_router
from app.modules.challenge.challenge_controller import router as challenge_router
from app.modules.users.user_controller import router as user_router
from app.modules.checkins.checkin_controller import router as checkin_router


app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Permite todas as origens (trocar por lista específica em produção)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

Base.metadata.create_all(bind=engine)

# Incluindo routers
app.include_router(auth_router)
app.include_router(challenge_router)
app.include_router(user_router)
app.include_router(checkin_router)


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
