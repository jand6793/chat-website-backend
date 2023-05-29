from app import common
from app.database.connection import crud
from app.database.repositories.users import funcs as userFuncs
from app.database.repositories.users import models as userModels
from app.database.repositories.messages import (
    models as messageModels,
    ITEM_TYPE,
    BASE_PROPERTIES,
)
from app.models import baseModels


def get_messages(
    message_criteria: messageModels.MessageCriteria, user_id: int | None = None
):
    criteria, values = create_message_criteria_key_value_pairs(
        message_criteria, user_id
    )
    sort_by = baseModels.create_sort_by(ITEM_TYPE, message_criteria.sort_by)
    return crud.select(ITEM_TYPE, BASE_PROPERTIES, criteria, values, sort_by)


def create_message_criteria_key_value_pairs(
    message_criteria: messageModels.MessageCriteria, user_id: int | None
):
    criteria_results = create_criteria_key_value_pairs(
        message_criteria, user_id
    )
    criteria_keys, criteria_values = common.unzip(criteria_results)
    joined_criteria = common.join_with_and(criteria_keys)
    return joined_criteria, criteria_values


def create_criteria_key_value_pairs(
    message_criteria: messageModels.MessageCriteria, user_id: int | None
):
    criteria = [
        (
            f"({ITEM_TYPE}.source_user_id = %s OR {ITEM_TYPE}.target_user_id = %s)",
            user_id or "",
        ),
        baseModels.create_equals_non_string_string(
            ITEM_TYPE,
            "source_user_id",
            message_criteria.source_user_id,
            message_criteria.exclude_source_user_id,
        ),
        baseModels.create_equals_non_string_string(
            ITEM_TYPE,
            "target_user_id",
            message_criteria.target_user_id,
            message_criteria.exclude_target_user_id,
        ),
        baseModels.create_similar_to_string(
            ITEM_TYPE,
            "content",
            message_criteria.content,
            message_criteria.exclude_content,
        ),
    ] + baseModels.create_base_property_criterias(ITEM_TYPE, message_criteria)
    return common.get_true_values(criteria)


def create_message(
    user: userModels.User,
    message: messageModels.MessageToDB,
    return_results: bool = False,
):
    other_user_ids = {message.source_user_id, message.target_user_id} - {user.id}
    users = userFuncs.get_users_by_ids(other_user_ids)
    if len(users.records) != 1:
        return users.new(error=ValueError("Invalid source or target user ids"))
    return crud.insert(ITEM_TYPE, message, return_results)


def update_message(
    message_id: int, message: messageModels.MessageUpdate, return_results: bool = True
):
    return crud.update(ITEM_TYPE, message_id, message, return_results)


def delete_message(
    conversation_id: int, delete: bool = True, return_results: bool = True
):
    return crud.delete(ITEM_TYPE, conversation_id, delete, return_results)
