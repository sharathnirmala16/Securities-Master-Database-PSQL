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
    try:
        tables: List[str] = securities_master.get_all_tables()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@app.get("/{table_name}/get-table")
async def get_table(table_name: str, dependencies=Depends(JWTBearer())):
    try:
        if table_name not in securities_master.get_all_tables():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Table not found"
            )

        table = securities_master.get_table(table_name)

        if pd.api.types.is_datetime64_any_dtype(table.index.to_series()):
            table.index = table.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        for column in table.columns:
            if pd.api.types.is_datetime64_any_dtype(table[column]):
                table[column] = table[column].dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        return JSONResponse(content=table.to_dict(orient="records"))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete("/{table_name}/delete-table")
async def delete_table(table_name: str):
    if table_name not in securities_master.get_all_tables():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Table not found"
        )
    try:
        securities_master.delete_table(table_name)
        return {"message": "table deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/{table_name}/add-row")
async def add_rows(table_name: str, row_data: Dict[str, int | float | str | None]):
    if table_name not in securities_master.get_all_tables():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Table not found"
        )
    if (
        list(row_data.keys())
        == securities_master.get_table(table_name).columns.to_list()
    ):
        try:
            securities_master.add_row(table_name, row_data)
            return {"message": "Added a new row successfully"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rows"
        )


@app.put("/{table_name}/edit-row")
async def edit_row(
    table_name: str,
    old_row_data: Dict[str, int | float | str | None],
    new_row_data: Dict[str, int | float | str | None],
):
    if table_name not in securities_master.get_all_tables():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Table not found"
        )
    if set(new_row_data.keys()).issubset(
        set(securities_master.get_table(table_name).columns.to_list())
    ):
        try:
            securities_master.edit_row(table_name, old_row_data, new_row_data)
            return {"message": "Edited a row successfully"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rows"
        )


@app.delete("/{table_name}/delete-row")
async def delete_row(table_name: str, row_data: Dict):
    if table_name not in securities_master.get_all_tables():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Table not found"
        )
    try:
        securities_master.delete_row(table_name, row_data)
        return {"message": "Row deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/get-prices")
async def get_prices(
    interval: int,
    start_datetime: str,
    end_datetime: str,
    vendor: str,
    exchange: str,
    instrument: str,
    tickers: List[str] = [],
    index: str = "",
    vendor_login_credentials: Dict[str, str] = {},
    cache_data=False,
):
    try:
        data: Dict[str, pd.DataFrame] = securities_master.get_prices(
            interval=interval,
            start_datetime=datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S"),
            vendor=vendor,
            exchange=exchange,
            instrument=instrument,
            tickers=None if tickers == [] else tickers,
            index=None if index == "" else index,
            vendor_login_credentials=vendor_login_credentials,
            cache_data=cache_data,
        )

        for ticker in data:
            table = data[ticker].copy(deep=True)
            if pd.api.types.is_datetime64_any_dtype(table.index.to_series()):
                table.index = table.index.to_series().dt.strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )
            for column in table.columns:
                if pd.api.types.is_datetime64_any_dtype(table[column]):
                    table[column] = table[column].dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            data[ticker] = table.reset_index(drop=False).to_dict(orient="records")
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
