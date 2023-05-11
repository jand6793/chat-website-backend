import datetime

from fastapi import status, APIRouter, HTTPException, Depends, Query
from pydantic import error_wrappers

from app.database.repositories.messages import (
    funcs as messageFuncs,
    models as messageModels,
)
from app.database.repositories.users import models as userModels
from app.database.connection import database
from app.models import modelExceptionFuncs
from app.models.validatorFuncs import ValidateId
from app.services import authentication as auth


router = APIRouter(prefix="/messages")


@router.get("", status_code=status.HTTP_200_OK)
async def get_messages(
    id: int | None = None,
    exclude_id: bool = False,
    source_user_id: int | None = None,
    exclude_source_user_id: bool = False,
    target_user_id: int | None = None,
    exclude_target_user_id: bool = False,
    content: str | None = None,
    exclude_content: bool = False,
    created: tuple[datetime.datetime, datetime.datetime] | None = Query(None),
    exclude_created: bool = False,
    last_modified: tuple[datetime.datetime, datetime.datetime] | None = Query(None),
    exclude_last_modified: bool = False,
    deleted: bool | None = None,
    sort_by: str | None = None,
    user: userModels.User = Depends(auth.get_current_user),
):
    try:
        message_criteria = messageModels.MessageCriteria(
            id=id,
            exclude_id=exclude_id,
            source_user_id=source_user_id,
            exclude_source_user_id=exclude_source_user_id,
            target_user_id=target_user_id,
            exclude_target_user_id=exclude_target_user_id,
            content=content,
            exclude_content=exclude_content,
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
        results = await messageFuncs.get_messages(user.id, message_criteria)
        if not results.records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No messages found with the given criteria.",
            )
        return {"items": results.records}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_message(
    message: messageModels.MessageCreate,
    return_results: bool = False,
    user: userModels.User = Depends(auth.get_current_user),
):
    message_to_db = messageModels.MessageToDB(
        **message.dict() | {"source_user_id": user.id}
    )
    results = await messageFuncs.create_message(message_to_db, return_results)
    return results.records[0] if return_results else None


@router.patch("/{message_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_message(
    message_update: messageModels.MessageUpdate,
    message_id: int = ValidateId,
    return_results: bool = False,
    user: userModels.User = Depends(auth.get_current_user),
):
    message = await get_message_from_id(message_id)
    verify_message_exists(message)
    verify_user_is_message_owner(user, message)
    results = await messageFuncs.update_message(
        message_id, message_update, return_results
    )
    return results.records[0] if return_results else None


@router.delete("/{message_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_message(
    message_id: int = ValidateId,
    delete: bool = False,
    return_results: bool = False,
    user: userModels.User = Depends(auth.get_current_user),
):
    message = await get_message_from_id(message_id)
    verify_message_exists(message)
    verify_user_is_message_owner(user, message)
    results = await messageFuncs.delete_message(message_id, delete, return_results)
    return results.records[0] if return_results else None


def verify_message_exists(message: database.ExecResult):
    if not message.records[0]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No message found with the given id",
        )


def verify_user_is_message_owner(user: userModels.User, message: database.ExecResult):
    if message.records[0]["source_user_id"] != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this message",
        )


async def get_message_from_id(message_id: int):
    message_criteria = messageModels.MessageCriteria(id=message_id)
    return await messageFuncs.get_messages(message_criteria)
