from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserOut(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
