from app import common
from app.database.connection import crud
from app.database.repositories.messages import (
    models as messageModels,
    ITEM_TYPE,
    BASE_PROPERTIES,
)
from app.models import baseModels


async def get_messages(user_id: int, message_criteria: messageModels.MessageCriteria):
    set_message_criteria = message_criteria.copy(update={"deleted": False})
    criteria, values = create_message_criteria_string(user_id, set_message_criteria)
    sort_by = baseModels.create_sort_by(ITEM_TYPE, set_message_criteria.sort_by)
    return await crud.select(ITEM_TYPE, BASE_PROPERTIES, criteria, values, sort_by)


def create_message_criteria_string(
    user_id: int, message_criteria: messageModels.MessageCriteria
):
    criteria_results = create_criteria_strs(user_id, message_criteria)
    criteria = common.get_true_values(criteria_results)
    joined_criteria = common.join_with_and(criteria)
    all_values = [
        user_id,
        user_id,
        message_criteria.source_user_id,
        message_criteria.target_user_id,
        message_criteria.content,
    ]
    values = common.get_true_values(all_values)
    return joined_criteria, values


def create_criteria_strs(user_id: int, message_criteria: messageModels.MessageCriteria):
    return [
        "(source_user_id = %s OR target_user_id = %s)",
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


async def create_message(
    message: messageModels.MessageToDB, return_results: bool = False
):
    return await crud.insert(ITEM_TYPE, message, return_results)


async def update_message(
    message_id: int, message: messageModels.MessageUpdate, return_results: bool = True
):
    return await crud.update(ITEM_TYPE, message_id, message, return_results)


async def delete_message(
    conversation_id: int, delete: bool = True, return_results: bool = True
):
    return await crud.delete(ITEM_TYPE, conversation_id, delete, return_results)
