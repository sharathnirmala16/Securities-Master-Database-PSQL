from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class RequestDetails(BaseModel):
    username: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class ChangePassword(BaseModel):
    username: str
    old_password: str
    new_password: str


class TokenCreate(BaseModel):
    username: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime
