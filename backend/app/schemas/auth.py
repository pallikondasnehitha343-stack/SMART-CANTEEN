from typing import Optional
from pydantic import BaseModel
from app.models.user import UserRole
from datetime import datetime

class UserRegister(BaseModel):
    campus_id: str
    full_name: str
    email: str
    password: str
    role: Optional[UserRole] = UserRole.STUDENT
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    campus_id: str
    full_name: str
    email: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
