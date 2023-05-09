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


class SourceItem(pydantic.BaseModel):
    id: int
    item_type: str


class ItemLinks(pydantic.BaseModel):
    id: int
    item_type: str
    link_type: str | None = None
    source_items: tuple[SourceItem, ...]


class ItemsLinks(pydantic.BaseModel):
    items_links: tuple[ItemLinks, ...]


class PaginationBase(pydantic.BaseModel):
    sort_by: str | None = None

    # @pydantic.root_validator()
    # def validate_all(cls: "PaginationBase", values: dict[str, int | str | None]):
    #     return validate_all_properties_are_specified(values)


class BasePropertiesCriteria(pydantic.BaseModel):
    created: tuple[datetime, datetime] | None = None
    exclude_created: bool = False
    last_modified: tuple[datetime, datetime] | None = None
    exclude_last_modified: bool = False
    deleted: bool | None = None


class PaginationBaseProperties(PaginationBase, BasePropertiesCriteria):
    pass
    # @pydantic.root_validator()
    # def validate_all(
    #     cls: "PaginationBaseProperties", values: dict[str, int | str | None]
    # ):
    #     if values["cursor"] and values["cursor"].count(",") > 1:
    #         raise ValueError(
    #             "sort_by can't have multiple properties when cursor is specified"
    #         )
    #     else:
    #         return values


def create_items_links(item_links: tuple[ItemLinks, ...]):
    return ItemsLinks(items_links=item_links)


def create_base_property_criterias(
    item_type: str,
    item: PaginationBaseProperties | IdCriteria,
):
    return [
        create_id_string(item_type, item.id, item.exclude_id),
        create_datetime_datetime_string(
            item_type, "created", item.created, item.exclude_created
        ),
        create_datetime_datetime_string(
            item_type, "last_modified", item.last_modified, item.exclude_last_modified
        ),
        create_deleted_criteria_string(item_type, item.deleted),
    ]


def create_similar_to_string(
    item_type: str, property: str, value: str | None, exclude: bool = False
):
    statement = f"({item_type}.{property} SIMILAR TO '%%s%')" if value else ""
    return wrap_statement_if_exclude_string(statement, exclude)


def create_equals_string_string(
    item_type: str, property: str, value: str | None, exclude: bool = False
):
    statement = f"({item_type}.{property} = %s)" if value else ""
    return wrap_statement_if_exclude_string(statement, exclude)


def create_equals_non_string_string(
    item_type: str, property: str, value: Any, exclude: bool = False
):
    statement = f"{item_type}.{property} = {value}" if value is not None else ""
    return wrap_statement_if_exclude_string(statement, exclude)


def create_id_string(item_type: str, id: int, exclude: bool = False):
    query_string = f"({item_type}.id = {id})" if id else ""
    return wrap_statement_if_exclude_string(query_string, exclude)


def create_datetime_datetime_string(
    item_type: str,
    property: str,
    range: tuple[datetime, datetime] | tuple[time.struct_time, time.struct_time] | None,
    exclude: bool = False,
):
    base_str = f"{item_type}.{property}"
    statement = (
        f"({base_str} >= '{range[0]}' AND {base_str} <= '{range[1]}')" if range else ""
    )
    return wrap_statement_if_exclude_string(statement, exclude)


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
