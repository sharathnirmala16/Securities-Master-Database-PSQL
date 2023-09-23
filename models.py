from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    username = Column(String(32), nullable=False, primary_key=True)
    password = Column(String(256), unique=True, nullable=False)


class TokenTable(Base):
    __tablename__ = "token"
    username = Column(String(32))
    access_token = Column(String(512), primary_key=True)
    refresh_token = Column(String(512), nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.now)
