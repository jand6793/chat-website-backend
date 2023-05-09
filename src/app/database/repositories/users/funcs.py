from typing import Any

from app.database.repositories.users import models as userModels
from app.models import baseModels
from app.services import authentication
from app.database.connection import crud
from app.database.repositories.users import ITEM_TYPE, BASE_PROPERTIES
from app import common


async def get_users(user_criteria: userModels.UserCriteria, is_login: bool = False):
    criteria, values = create_user_criteria_string(user_criteria, is_login)
    sort_by = baseModels.create_sort_by(ITEM_TYPE, user_criteria.sort_by)
    properties = BASE_PROPERTIES + (["hashed_password"] if is_login else [])
    results = await crud.select(ITEM_TYPE, properties, criteria, values, sort_by)
    return results.records


def create_user_criteria_string(
    user_criteria: userModels.UserCriteria, logging_in: bool
):
    criteria_results = (
        baseModels.create_similar_to_string(
            ITEM_TYPE,
            "full_name",
            user_criteria.full_name,
            user_criteria.exclude_full_name,
        ),
        create_username_criteria_string(
            user_criteria.username, logging_in, user_criteria.exclude_username
        ),
        baseModels.create_similar_to_string(
            ITEM_TYPE,
            "description",
            user_criteria.description,
            user_criteria.exclude_description,
        ),
        *baseModels.create_base_property_criterias(ITEM_TYPE, user_criteria),
    )
    criteria = [criteria for criteria in criteria_results if criteria]
    joined_criteria = " AND ".join(criteria) if criteria else ""
    all_values = (
        user_criteria.full_name,
        user_criteria.username,
        user_criteria.description,
    )
    values = common.get_true_values(all_values)
    return joined_criteria, values


def create_username_criteria_string(
    username: str | None, logging_in: bool, exclude: bool = False
):
    return (
        baseModels.create_equals_string_string(ITEM_TYPE, "username", username, exclude)
        if logging_in
        else baseModels.create_similar_to_string(
            ITEM_TYPE, "username", username, exclude
        )
    )


def create_title_criteria_string(title: str | None, exclude: bool = False):
    if title:
        titleFuncs.get_titles(titleModels.TitleCriteria(name=title))
        statement = baseModels.create_similar_to_string(ITEM_TYPE, "title", title)
    else:
        statement = ""
    return baseModels.wrap_statement_if_exclude_string(statement, exclude)


async def create_users(users: userModels.UsersCreate, return_results: bool = False):
    users_to_db = [create_user_to_db(user) for user in users.users]
    results = await crud.insert(ITEM_TYPE, users_to_db, return_results)
    return remove_hashed_passwords(results.records)


def remove_hashed_passwords(items: list[dict[str, Any]]):
    return [{k: v for k, v in item.items() if k != "hashed_password"} for item in items]


def create_user_to_db(user: userModels.UserCreate):
    hashed_password = authentication.hash_password(user.password)
    combined_user = user.dict() | {"hashed_password": hashed_password}
    return userModels.UserToDB(**combined_user)


def update_user(user: userModels.UserUpdate, return_results: bool = True):
    user_to_db = create_user_update_to_db(user)
    return storageEndpointFuncs.update_item(
        user.id, ITEM_TYPE, user_to_db, return_results
    )


def create_user_update_to_db(
    user: userModels.UserUpdate,
):
    if user.password:
        hashed_password = authentication.hash_password(user.password)
        combined_user = user.dict(exclude_none=True) | {
            "hashed_password": hashed_password
        }
    else:
        combined_user = user.dict(exclude_none=True)
    return userModels.UserUpdateToDB(**combined_user)


def delete_user(
    user_id: baseModels.Id, delete: bool = True, return_results: bool = True
):
    ids = baseModels.Ids(ids=(user_id.id,))
    currentStateFuncs.delete_current_state(user_id, delete)
    return storageEndpointFuncs.delete_items(ITEM_TYPE, ids, delete, return_results)
