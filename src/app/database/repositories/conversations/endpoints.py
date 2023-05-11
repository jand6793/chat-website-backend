import datetime

from fastapi import status, APIRouter, HTTPException, Depends, Query
from pydantic import error_wrappers

from app.database.repositories.messages import (
    funcs as messageFuncs,
    models as messageModels,
)
from app.database.repositories.users import funcs as userFuncs
from app.database.repositories.users import models as userModels
from app.services import authentication as auth


router = APIRouter()


@router.get("/conversations", status_code=status.HTTP_200_OK)
async def get_conversations(
    user: userModels.User = Depends(auth.get_current_user),
):
    message_criteria = messageModels.MessageCriteria()
    messages = await messageFuncs.get_messages(message_criteria, user.id)
    source_user_ids = {message["source_user_id"] for message in messages.records}
    target_user_ids = {message["target_user_id"] for message in messages.records}
    combined_user_ids = source_user_ids | target_user_ids
    other_user_ids = combined_user_ids - {user.id}
    users = await userFuncs.get_users_by_ids(other_user_ids)
    return [
        {
            "user": user,
            "messages": [
                message
                for message in messages.records
                if user["id"] in (message["source_user_id"], message["target_user_id"])
            ],
        }
        for user in users.records
    ]
