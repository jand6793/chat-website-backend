from typing import Any

from app import common
from app.database.connection import crud
from app.database.repositories.users import (
    models as userModels,
    ITEM_TYPE,
    BASE_PROPERTIES,
)
from app.models import baseModels
from app.services import authentication


async def get_users(user_criteria: userModels.UserCriteria, is_login: bool = False):
    set_user_criteria = user_criteria.new(deleted=False)
    criteria, values = create_user_criteria_string(set_user_criteria, is_login)
    sort_by = baseModels.create_sort_by(ITEM_TYPE, set_user_criteria.sort_by)
    properties = combined_properties(is_login)
    results = await crud.select(ITEM_TYPE, properties, criteria, values, sort_by)
    return results.records


def create_user_criteria_string(
    user_criteria: userModels.UserCriteria, logging_in: bool
):
    criteria_results = create_criteria_strs(user_criteria, logging_in)
    criteria = common.get_true_values(criteria_results)
    joined_criteria = join_with_and(criteria)
    all_values = [
        user_criteria.full_name,
        user_criteria.username,
        user_criteria.description,
    ]
    values = common.get_true_values(all_values)
    return joined_criteria, values


def create_criteria_strs(user_criteria: userModels.UserCriteria, logging_in: bool):
    return [
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
    ] + baseModels.create_base_property_criterias(ITEM_TYPE, user_criteria)


def combined_properties(is_login: bool):
    return BASE_PROPERTIES + (["hashed_password"] if is_login else [])


def join_with_and(criteria: list[str]):
    return " AND ".join(criteria) if criteria else ""


def create_username_criteria_string(
    username: str | None, logging_in: bool, exclude: bool = False
):
    params = ITEM_TYPE, "username", username, exclude
    if logging_in:
        return baseModels.create_equals_string_string(*params)
    else:
        return baseModels.create_similar_to_string(*params)


async def create_user(user: userModels.UserCreate, return_results: bool = False):
    user_to_db = create_user_to_db(user)
    results = await crud.insert(ITEM_TYPE, user_to_db, return_results)
    if results.error:
        return results
    return results.new(remove_hashed_passwords(results.records))


def remove_hashed_passwords(items: list[dict[str, Any]]):
    return [{k: v for k, v in item.items() if k != "hashed_password"} for item in items]


def create_user_to_db(user: userModels.UserCreate):
    hashed_password = authentication.hash_password(user.password)
    combined_user = user.dict() | {"hashed_password": hashed_password}
    return userModels.UserToDB(**combined_user)


async def update_user(
    user_id: int, user: userModels.UserUpdate, return_results: bool = True
):
    user_to_db = add_hashed_password(user)
    filtered_user_to_db = user_to_db.dict(exclude_unset=True)
    return await crud.update(ITEM_TYPE, user_id, filtered_user_to_db, return_results)


def add_hashed_password(user: userModels.UserUpdate):
    filtered_user = user.dict(exclude_unset=True)
    if user.password:
        hashed_password = authentication.hash_password(user.password)
        user_with_hash = filtered_user | {"hashed_password": hashed_password}
    else:
        user_with_hash = filtered_user
    return userModels.UserUpdateToDB(**user_with_hash)


def delete_user(user_id: int, delete: bool = True, return_results: bool = True):
    return crud.delete(ITEM_TYPE, user_id, delete, return_results)
