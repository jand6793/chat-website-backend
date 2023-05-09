import datetime
from typing import Any

import fastapi
from fastapi import security, status
from pydantic import error_wrappers

from app.services import authentication
from app.models import baseModels, modelExceptionFuncs
from app.models import validatorFuncs
from app.core import config
from app.database.repositories.users import funcs as userFuncs, models as userModels

router = fastapi.APIRouter()


@router.post("/token", response_model=userModels.Token)
async def login_for_access_token(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
):
    if user := await authentication.authenticate_user(
        form_data.username, form_data.password
    ):
        access_token_expires = datetime.timedelta(
            minutes=config.config.access_token_expire_minutes
        )
        access_token = authentication.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise fastapi.HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/users/me", response_model=userModels.User)
async def read_users_me(
    current_user: userModels.User = fastapi.Depends(authentication.get_current_user),
):
    return current_user


@router.get("/users", status_code=status.HTTP_200_OK)
async def get_users(
    id: int | None = None,
    full_name: str | None = None,
    exclude_full_name: bool = False,
    username: str | None = None,
    exclude_username: bool = False,
    description: str | None = None,
    exclude_description: bool = False,
    created: tuple[datetime.datetime, datetime.datetime] | None = fastapi.Query(None),
    exclude_created: bool = False,
    last_modified: tuple[datetime.datetime, datetime.datetime]
    | None = fastapi.Query(None),
    exclude_last_modified: bool = False,
    deleted: bool | None = None,
    sort_by: str | None = None,
    user: userModels.User = fastapi.Depends(authentication.get_current_user),
):
    try:
        user_criteria = userModels.UserCriteria(
            id=id,
            full_name=full_name,
            exclude_full_name=exclude_full_name,
            username=username,
            exclude_username=exclude_username,
            description=description,
            exclude_description=exclude_description,
            created=created,
            exclude_created=exclude_created,
            last_modified=last_modified,
            exclude_last_modified=exclude_last_modified,
            deleted=deleted,
            sort_by=sort_by,
        )
    except error_wrappers.ValidationError as e:
        modelExceptionFuncs.raise_model_exception(e)
    else:
        return {"results": userFuncs.get_users(user_criteria)}


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_users(new_users: userModels.UsersCreate, return_results: bool = False):
    return await userFuncs.create_users(new_users, return_results)


@router.patch("/users", status_code=status.HTTP_202_ACCEPTED)
async def update_user(
    user_update: userModels.UserUpdate,
    return_results: bool = False,
    user: userModels.User = fastapi.Depends(authentication.get_current_user),
):
    return userFuncs.update_user(user_update, return_results)


@router.delete("/users", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(
    id: baseModels.Id,
    delete: bool = False,
    return_results: bool = False,
    user: userModels.User = fastapi.Depends(authentication.get_current_user),
):
    return userFuncs.delete_user(id, delete, return_results)
