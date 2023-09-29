import jwt
import schemas
import models
import pandas as pd

from models import User
from database import Base, engine, local_session
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from auth_bearer import JWTBearer
from functools import wraps
from utils import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_hashed_password,
    JWT_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY,
    ALGORITHM,
)
from typing import Dict, List
from securities_master import SecuritiesMaster
from credentials import psql_credentials
from datetime import datetime


Base.metadata.create_all(engine)


def get_session() -> None:
    session = local_session()
    try:
        yield session
    finally:
        session.close()


securities_master = SecuritiesMaster(
    psql_credentials["host"],
    psql_credentials["port"],
    psql_credentials["username"],
    psql_credentials["password"],
)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
async def register_user(
    user: schemas.UserCreate, session: Session = Depends(get_session)
) -> Dict:
    existing_user = session.query(User).filter_by(username=user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = models.User(
        username=user.username, password=get_hashed_password(user.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": f"User {new_user.username} created successfully"}


@app.post("/login", response_model=schemas.TokenSchema)
async def login(
    request: schemas.RequestDetails, db: Session = Depends(get_session)
) -> Dict:
    user: User = db.query(User).filter(User.username == request.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username"
        )
    hashed_password = user.password
    if not verify_password(request.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    access = create_access_token(user.username)
    refresh = create_refresh_token(user.username)

    token_db = models.TokenTable(
        username=user.username, access_token=access, refresh_token=refresh, status=True
    )

    db.add(token_db)
    db.commit()
    db.refresh(token_db)

    return {
        "access_token": access,
        "refresh_token": refresh,
    }


@app.post("/change-password")
async def change_password(
    request: schemas.ChangePassword,
    dependencies=Depends(JWTBearer()),
    db: Session = Depends(get_session),
):
    user: User = (
        db.query(models.User).filter(models.User.username == request.username).first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
        )

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()

    return {"message": "Password changed successfully"}


@app.post("/logout")
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    username = payload["sub"]
    token_record = db.query(models.TokenTable).all()
    info = []
    for record in token_record:
        if (datetime.utcnow() - record.created_date).days > 1:
            info.append(record.username)
    if info:
        existing_token = (
            db.query(models.TokenTable)
            .where(models.TokenTable.username.in_(info))
            .delete()
        )
        db.commit()

    existing_token = (
        db.query(models.TokenTable)
        .filter(
            models.TokenTable.username == username,
            models.TokenTable.access_token == token,
        )
        .first()
    )
    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message": "Logout Successfully"}


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = jwt.decode(kwargs["dependencies"], JWT_SECRET_KEY, ALGORITHM)
        username = payload["sub"]
        data = (
            kwargs["session"]
            .query(models.TokenTable)
            .filter_by(
                username=username, access_toke=kwargs["dependencies"], status=True
            )
            .first()
        )
        if data:
            return func(kwargs["dependencies"], kwargs["session"])

        else:
            return {"msg": "Token blocked"}

    return wrapper


@app.get("/get-all-tables")
async def get_all_tables(dependencies=Depends(JWTBearer())):
    tables: List[str] = securities_master.get_all_tables()
    return {"tables": tables}


@app.get("/get-table/{table_name}")
async def get_table(table_name: str, dependencies=Depends(JWTBearer())):
    if table_name not in securities_master.get_all_tables():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Table not found"
        )
    table = securities_master.get_table(table_name).to_dict(orient="records")
    return JSONResponse(content=table)
