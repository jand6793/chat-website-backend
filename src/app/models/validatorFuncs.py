import datetime
import functools
from typing import Any, Annotated

from fastapi import Path


ONE_LESS_16_BIT_INT = 2**15 - 1
ONE_LESS_32_BIT_INT = 2**31 - 1
ONE_LESS_64_BIT_INT = 2**63 - 1
MAX_DECIMAL_PLACES_FOR_FLOAT = 16
MAX_HOURS = 100_000
MAX_NOTES_LENGTH = 500

ValidateId = Annotated[int, Path(gt=0, le=ONE_LESS_64_BIT_INT)]


def validate_float_decimal_places(value: float | None, value_name: str):
    if value and not 0 <= len(str(value).split(".")[1]) <= MAX_DECIMAL_PLACES_FOR_FLOAT:
        raise ValueError(
            f"{value_name} {value} is not between 0 and {MAX_DECIMAL_PLACES_FOR_FLOAT} decimal places"
        )
    else:
        return value


def validate_between_values(
    value: int | float | None,
    min_value: int | float,
    max_value: int | float,
    value_name: str,
):
    """Inclusive min and max"""
    if value and not (min_value <= value <= max_value):
        raise ValueError(f"{value_name} must be between {min_value} and {max_value}")
    else:
        return value


def validate_16_bit_id(value: int | None):
    return validate_between_values(value, 1, ONE_LESS_16_BIT_INT, "id")


def validate_16_bit_ids(ids: tuple[int, ...] | None):
    if ids:
        for id in ids:
            validate_16_bit_id(id)
    return ids


def validate_32_bit_id(value: int | None):
    return validate_between_values(value, 1, ONE_LESS_32_BIT_INT, "id")


def validate_32_bit_ids(ids: tuple[int, ...] | None):
    if ids:
        for id in ids:
            validate_32_bit_id(id)
    return ids


def validate_64_bit_id(value: int | None):
    return validate_between_values(value, 1, ONE_LESS_64_BIT_INT, "id")


def validate_64_bit_ids(ids: tuple[int, ...] | None):
    if ids:
        for id in ids:
            validate_64_bit_id(id)
    return ids


def validate_price(price: float | None):
    validate_float_decimal_places(price, "price")
    validate_between_values(price, 0, ONE_LESS_32_BIT_INT, "price")
    return price


def validate_prices(prices: tuple[float, ...] | None):
    if prices:
        for price in prices:
            validate_price(price)
    return prices


def validate_time_in_hours(hour: float | None):
    validate_float_decimal_places(hour, "hour")
    validate_between_values(hour, 0, MAX_HOURS, "hour")
    return hour


def validate_times_in_hours(hours: tuple[float, ...] | None):
    if hours:
        for hour in hours:
            validate_time_in_hours(hour)
    return hours


def validate_string_length(
    string: str | None, min_length: int, max_length: int, string_name: str
):
    """Inclusive min and max"""
    if string and min_length > len(string) > max_length:
        raise ValueError(
            f"{string_name} must be between {min_length} and {max_length} characters"
        )
    else:
        return string


def validate_string_passage(string_passage: str | None):
    return validate_string_length(string_passage, 1, 10_000, "string_passage")


def validate_string_id(string_id: str | None):
    return validate_string_length(string_id, 1, 50, "string_id")


def validate_notes(notes: str | None):
    return validate_string_length(notes, 1, MAX_NOTES_LENGTH, "notes")


def validate_string_name(string_name: str | None):
    if string_name is not None:
        return validate_string_length(string_name, 1, 100, "string_name")
    else:
        return None


def validate_quantity(quantity: int | None):
    return validate_between_values(quantity, 1, ONE_LESS_32_BIT_INT, "quantity")


def validate_line_number(line_number: int | None):
    return validate_between_values(line_number, 1, ONE_LESS_32_BIT_INT, "line_number")


def validate_reference_number(reference_number: int | None):
    return validate_between_values(
        reference_number, 100_000, ONE_LESS_32_BIT_INT, "reference_number"
    )


def validate_due_dates(due_dates: tuple[datetime.datetime, ...] | None):
    if due_dates and not functools.reduce(validate_pre_post_datetimes, due_dates):
        raise ValueError("due_dates must be in ascending order")
    return due_dates


def validate_pre_post_datetimes(
    pre_datetime: datetime.datetime | None, post_datetime: datetime.datetime
):
    return post_datetime if pre_datetime and pre_datetime <= post_datetime else True


def validate_single_property_specified(
    values: dict[str, Any], property_names: tuple[str, ...] | None = None
):
    values_to_check = (
        values
        if property_names is None
        else tuple(value for key, value in values.items() if key in property_names)
    )
    if sum(map(value_is_not_none, values_to_check)) <= 1:
        return values
    property_names_joined = (
        ", ".join(property_names) if property_names else ", ".join(values.keys())
    )
    error_message = f"{property_names_joined} are mutually exclusive"
    raise ValueError(error_message)


def value_is_not_none(value: Any):
    return value is not None
