from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)
    user_type: str = "solicitante"

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    user_type: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str