from pydantic import BaseModel, EmailStr
from typing import Optional

class Create_Todo(BaseModel):
    title: str

class Update_Todo(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


# ── Auth Schemas ──

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str