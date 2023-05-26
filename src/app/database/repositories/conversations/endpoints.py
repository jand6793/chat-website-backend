from typing import Any

from fastapi import status, APIRouter, Depends
from app.database.repositories.messages import (
    funcs as messageFuncs,
    models as messageModels,
)
from app.database.repositories.users import funcs as userFuncs
from app.database.repositories.users import models as userModels
from app.services import authentication as auth


router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.get("", status_code=status.HTTP_200_OK)
def get_conversations(
    user: userModels.User = Depends(auth.get_current_user),
):
    message_criteria = messageModels.MessageCriteria()
    messages = messageFuncs.get_messages(message_criteria, user.id)
    source_user_ids = {message["source_user_id"] for message in messages.records}
    target_user_ids = {message["target_user_id"] for message in messages.records}
    combined_user_ids = source_user_ids | target_user_ids
    other_user_ids = combined_user_ids - {user.id}
    users = userFuncs.get_users_by_ids(other_user_ids)
    return create_conversation_trees(messages.records, users.records)


def create_conversation_trees(
    messages: list[dict[str, Any]], users: list[dict[str, Any]]
):
    return [
        {
            "user": user,
            "messages": [
                message
                for message in messages
                if check_user_related_to_message(user, message)
            ],
        }
        for user in users
    ]


def check_user_related_to_message(user: dict[str, Any], message: dict[str, Any]):
    return user["id"] in (message["source_user_id"], message["target_user_id"])
