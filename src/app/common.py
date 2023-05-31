from typing import Any, Iterable, TypeVar
import functools

T = TypeVar("T")


def get_true_values(values: list[T]) -> list[T]:
    return [v for v in values if v]


def join_with_and(criteria: list[str]):
    return " AND ".join(criteria) if criteria else ""


def join_with_commas(values: Iterable[Any]):
    return ", ".join(str(v) for v in values) if values else ""


def unzip(items: Iterable[Iterable[T]]) -> list[list[T]]:
    return [list(t) for t in zip(*items)] if items else []


def add_any(
    container: tuple[Any, ...] | list[Any], value: Any
) -> tuple[Any, ...] | list[Any]:
    container_type = type(container)
    return container + container_type(value)


def flatten(container: tuple[Any, ...] | list[Any]):
    container_type = type(container)
    return container_type(functools.reduce(add_any, container, container_type()))
