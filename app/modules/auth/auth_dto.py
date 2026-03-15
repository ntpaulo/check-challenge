from pydantic import BaseModel, EmailStr


class RegisterRequestDTO(BaseModel):
    name: str
    email: EmailStr
    password: str
