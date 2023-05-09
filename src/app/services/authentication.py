import datetime
from datetime import timezone, timedelta, datetime

import fastapi
from fastapi import security, status
import jose
from jose import jwt
from passlib import context

from app.core.config import config
from app.database.repositories.users import funcs as userFuncs
from app.database.repositories.users import models as userModels


password_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str):
    return password_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return password_context.hash(password)


async def get_user(username: str):
    user_criteria = userModels.UserCriteria(username=username)
    if not (user_results := await userFuncs.get_users(user_criteria, True)):
        return None
    user = userModels.UserInDB(**user_results[0])
    return None if user.deleted else user


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if user and verify_password(password, user.hashed_password):
        return userModels.User(**user.dict())
    else:
        return None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode["exp"] = expire
    return jwt.encode(
        to_encode, config.secret_key.get_secret_value(), algorithm=config.jsw_algorithm
    )


credentials_exception = fastapi.HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = fastapi.Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, config.secret_key.get_secret_value(), algorithms=[config.jsw_algorithm]
        )

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        else:
            token_data = userModels.TokenData(username=username)
    except jose.JWTError as e:
        raise credentials_exception from e
    user = await get_user(token_data.username)
    if user is None:
        raise credentials_exception
    else:
        return userModels.User(**user.dict())
