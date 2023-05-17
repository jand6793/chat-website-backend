import datetime

from fastapi import status, APIRouter, HTTPException, Depends, Query
from psycopg import errors as pg_errors
from pydantic import error_wrappers

from app.database.repositories.users import funcs as userFuncs, models as userModels
from app.models import modelExceptionFuncs
from app.services import authentication as auth


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=userModels.User)
def read_user_me(user: userModels.User = Depends(auth.get_current_user)):
    return user


@router.get("", status_code=status.HTTP_200_OK)
def get_users(
    id: int | None = None,
    exclude_id: bool = False,
    full_name: str | None = None,
    exclude_full_name: bool = False,
    username: str | None = None,
    exclude_username: bool = False,
    description: str | None = None,
    exclude_description: bool = False,
    created: tuple[datetime.datetime, datetime.datetime] | None = Query(None),
    exclude_created: bool = False,
    last_modified: tuple[datetime.datetime, datetime.datetime] | None = Query(None),
    exclude_last_modified: bool = False,
    deleted: bool | None = None,
    sort_by: str | None = None,
    user: userModels.User = Depends(auth.get_current_user),
):
    try:
        user_criteria = userModels.UserCriteria(
            id=id,
            exclude_id=exclude_id,
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
        results = userFuncs.get_users(user_criteria)
        if not results.records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found with the given criteria.",
            )
        return {"items": results.records}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(new_user: userModels.UserCreate, return_results: bool = False):
    results = userFuncs.create_user(new_user, return_results)
    if not results.error:
        if return_results:
            return results.records[0]
    elif isinstance(results.error, pg_errors.UniqueViolation):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the given username already exists.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="An error occurred while creating the user.",
        )


@router.patch("/me", status_code=status.HTTP_202_ACCEPTED)
def update_user_me(
    user_update: userModels.UserUpdate,
    return_results: bool = False,
    user: userModels.User = Depends(auth.get_current_user),
):
    items = userFuncs.update_user(user.id, user_update, return_results)
    return items.records[0] if return_results else None


@router.delete("/me", status_code=status.HTTP_202_ACCEPTED)
def delete_user_me(
    delete: bool = False,
    return_results: bool = False,
    user: userModels.User = Depends(auth.get_current_user),
):
    results = userFuncs.delete_user(user.id, delete)
    return results.records[0] if return_results else None
