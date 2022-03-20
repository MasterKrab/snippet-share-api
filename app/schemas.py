from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class User(BaseModel):
    id: int
    username: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]
    old_password: Optional[str]


class UserOutput(User):
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class SnippetBase(BaseModel):
    code: str
    language: str


class SnippetCreate(BaseModel):
    code: str
    language: str


class SnippetUpdate(SnippetCreate):
    id: int


class SnippetOutput(SnippetBase):
    id: int
    created_at: datetime
    user: Optional[UserOutput] = None

    class Config:
        orm_mode = True
