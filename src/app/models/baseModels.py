from datetime import datetime
import time
from typing import Any

import pydantic

from app.models import validatorFuncs


def validate_atleast_one_property_is_specified(values: dict[str, Any]):
    if not any(values.values()):
        raise ValueError("At least one property must be specified")
    else:
        return values


def validate_all_properties_are_specified(values: dict[str, Any]):
    if not all(values.values()):
        raise ValueError("All properties must be specified")
    else:
        return values


class IdCriteria(pydantic.BaseModel):
    id: int | None = None
    exclude_id: bool = False

    _validate_id = pydantic.validator("id", allow_reuse=True)(
        validatorFuncs.validate_64_bit_id
    )


class Id(pydantic.BaseModel):
    id: int

    _validate_id = pydantic.validator("id", allow_reuse=True)(
        validatorFuncs.validate_64_bit_id
    )


class Ids(pydantic.BaseModel):
    ids: tuple[int, ...]

    _validate_ids = pydantic.validator("ids", allow_reuse=True)(
        validatorFuncs.validate_64_bit_ids
    )


class Deleted(pydantic.BaseModel):
    deleted: bool


class IdDeleted(Id, Deleted):
    pass


class PaginationBase(pydantic.BaseModel):
    sort_by: str | None = None


class BaseDates(pydantic.BaseModel):
    created: datetime
    last_modified: datetime


class BasePropertiesCriteria(pydantic.BaseModel):
    created: tuple[datetime, datetime] | None = None
    exclude_created: bool = False
    last_modified: tuple[datetime, datetime] | None = None
    exclude_last_modified: bool = False
    deleted: bool | None = None


class PaginationBaseProperties(PaginationBase, BasePropertiesCriteria):
    pass


def create_base_property_criterias(
    item_type: str,
    item: PaginationBaseProperties | IdCriteria,
) -> list[tuple[str, Any]]:
    id_criteria = create_id_string(item_type, item.id, item.exclude_id)
    id_criteria_pair = (id_criteria, item.id) if id_criteria else ()
    created_criteria = (
        create_datetime_datetime_string(
            item_type, "created", item.created, item.exclude_created
        ),
        item.created,
    )
    created_criteria_pair = created_criteria if created_criteria[0] else ()
    last_modified_criteria = (
        create_datetime_datetime_string(
            item_type,
            "last_modified",
            item.last_modified,
            item.exclude_last_modified,
        ),
        item.last_modified,
    )
    last_modified_criteria_pair = (
        last_modified_criteria if last_modified_criteria[0] else ()
    )
    deleted_criteria = (
        create_deleted_criteria_string(item_type, item.deleted),
        item.deleted,
    )
    deleted_criteria_pair = deleted_criteria if deleted_criteria[0] else ()
    criteria = [
        id_criteria_pair,
        created_criteria_pair,
        last_modified_criteria_pair,
        deleted_criteria_pair,
    ]
    return [c for c in criteria if c]


def create_similar_to_string(
    item_type: str, property: str, value: str | None, exclude: bool = False
):
    if value is None:
        return ()  # return the fornatted value "%{value}%" then test the request
    statement = f"({item_type}.{property} SIMILAR TO %s)"
    return wrap_statement_if_exclude_string(statement, exclude), f"%{value}%"


def create_equals_string_string(
    item_type: str, property: str, value: str | None, exclude: bool = False
):
    if value is None:
        return ()
    statement = f"({item_type}.{property} = %s)"
    return wrap_statement_if_exclude_string(statement, exclude), value


def create_equals_non_string_string(
    item_type: str, property: str, value: Any, exclude: bool = False
):
    if value is None:
        return ()
    statement = f"{item_type}.{property} = {value}"
    return wrap_statement_if_exclude_string(statement, exclude), value


def create_id_string(item_type: str, item_id: int | None, exclude: bool = False):
    if item_id is None:
        return ()
    query_string = f"({item_type}.id = {item_id})"
    return wrap_statement_if_exclude_string(query_string, exclude), item_id


def create_datetime_datetime_string(
    item_type: str,
    property: str,
    time_range: tuple[datetime, datetime]
    | tuple[time.struct_time, time.struct_time]
    | None,
    exclude: bool = False,
):
    if time_range is None:
        return ()
    base_str = f"{item_type}.{property}"
    statement = f"({base_str} >= '{time_range[0]}' AND {base_str} <= '{time_range[1]}')"
    return wrap_statement_if_exclude_string(statement, exclude), time_range


def wrap_statement_if_exclude_string(statement: str, exclude: bool):
    return f"(NOT {statement})" if statement and exclude else statement


def create_deleted_criteria_string(item_type: str, deleted: bool | None):
    return f"({item_type}.deleted = {deleted})" if deleted is not None else ""


def create_sort_by(item_type: str, sort_by: str | None):
    sort_by_string = ""
    if sort_by:
        sort_by_list = sort_by.split(",")
        for sort_by_index, sort_by_value in enumerate(sort_by_list):
            comma_string = ", " if sort_by_index > 0 else ""
            sort_by_string += f"{comma_string}{item_type}.{sort_by_value.strip()}"
    return f"{sort_by_string}" if sort_by else ""
