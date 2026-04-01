from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=128)
    phone: str | None = Field(default=None, max_length=20)

class UserLogin(BaseModel):
    identifier: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=128)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    phone: str | None
    role: str
    is_active: bool
    avatar_url: str | None
    created_at: datetime

class RegisterResponse(BaseModel):
    message: str
    user: UserPublic

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
