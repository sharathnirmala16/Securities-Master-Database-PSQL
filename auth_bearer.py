import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import TokenTable
from credentials import JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from typing import Any, Optional

ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 1 day
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"


def decodeJWT(jwtoken: str) -> Any | None:
    try:
        # Decode and verify the token
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except InvalidTokenError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


jwt_bearer = JWTBearer()
