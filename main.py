import schemas
import models
from models import User
from database import Base, engine, local_session
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from auth_bearer import JWTBearer
from functools import wraps
from utils import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_hashed_password,
)
from typing import Dict

Base.metadata.create_all(engine)


def get_session() -> None:
    session = local_session()
    try:
        yield session
    finally:
        session.close()


app = FastAPI()


@app.post("/register")
async def register_user(
    user: schemas.UserCreate, session: Session = Depends(get_session)
) -> Dict:
    existing_user = session.query(models.User).filter_by(username=user.username).first()
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


@app.get("/getusers")
def getusers(
    dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)
):
    users = session.query(models.User.username).all()
    return users


@app.post("/change-password")
def change_password(
    request: schemas.ChangePassword, db: Session = Depends(get_session)
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
