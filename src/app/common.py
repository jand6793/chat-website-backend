from typing import Any, Iterable, TypeVar

T = TypeVar("T")


def get_true_values(values: list[T]) -> list[T]:
    return [v for v in values if v]


def join_with_and(criteria: list[str]):
    return " AND ".join(criteria) if criteria else ""


def join_with_commas(values: Iterable[Any]):
    return ", ".join(str(v) for v in values) if values else ""
