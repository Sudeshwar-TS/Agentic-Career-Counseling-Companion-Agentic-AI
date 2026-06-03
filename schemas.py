from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ChatIn(BaseModel):
    question: str


class ProgressIn(BaseModel):
    progress_percent: float
