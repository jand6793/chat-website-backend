from typing import Any, Iterable

from app import common
from app.database.connection import crud
from app.database.connection.database import ExecResult
from app.database.repositories.users import (
    models as userModels,
    ITEM_TYPE,
    BASE_PROPERTIES,
)
from app.models import baseModels
from app.services import authentication


def get_users(user_criteria: userModels.UserCriteria, is_login: bool = False):
    criteria, values = create_user_criteria_key_value_pairs(user_criteria, is_login)
    sort_by = baseModels.create_sort_by(ITEM_TYPE, user_criteria.sort_by)
    properties = combined_properties(is_login)
    return crud.select(ITEM_TYPE, properties, criteria, values, sort_by)


def create_user_criteria_key_value_pairs(
    user_criteria: userModels.UserCriteria, logging_in: bool
):
    criteria_results = create_criteria_key_value_pairs(user_criteria, logging_in)
    if not criteria_results:
        return None, None
    criteria_keys, criteria_values = common.unzip(criteria_results)
    joined_criteria = common.join_with_and(criteria_keys)
    return joined_criteria, criteria_values


def create_criteria_key_value_pairs(
    user_criteria: userModels.UserCriteria, logging_in: bool
):
    criteria = [
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
    return common.get_true_values(criteria)


def combined_properties(is_login: bool):
    return BASE_PROPERTIES + (["hashed_password"] if is_login else [])


def create_username_criteria_string(
    username: str | None, logging_in: bool, exclude: bool = False
):
    params = ITEM_TYPE, "username", username, exclude
    if logging_in:
        return baseModels.create_equals_string_string(*params)
    else:
        return baseModels.create_similar_to_string(*params)


def get_users_by_ids(user_ids: Iterable[int], order_by: str = "id"):
    joined_ids = common.join_with_commas(user_ids)
    criteria = f"{ITEM_TYPE}.id IN ({joined_ids})"
    return crud.select(ITEM_TYPE, BASE_PROPERTIES, criteria, order_by=order_by)


def create_user(user: userModels.UserCreate, return_results: bool = False):
    user_to_db = create_user_to_db(user)
    results = crud.insert(ITEM_TYPE, user_to_db, return_results)
    if results.error:
        return results
    return ExecResult(remove_hashed_passwords(results.records))


def remove_hashed_passwords(items: list[dict[str, Any]]):
    return [{k: v for k, v in item.items() if k != "hashed_password"} for item in items]


def create_user_to_db(user: userModels.UserCreate):
    hashed_password = authentication.hash_password(user.password)
    combined_user = user.dict() | {"hashed_password": hashed_password}
    return userModels.UserToDB(**combined_user)


def update_user(user_id: int, user: userModels.UserUpdate, return_results: bool = True):
    user_to_db = add_hashed_password(user)
    filtered_user_to_db = user_to_db.dict(exclude_unset=True)
    return crud.update(ITEM_TYPE, user_id, filtered_user_to_db, return_results)


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
