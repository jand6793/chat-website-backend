from typing import Any

from pydantic import BaseModel

from app.database.connection.database import backend_exec as exec


async def select(
    table: str,
    properties: list[str],
    criteria: str = "",
    values: list[str] = [],
    order_by: str = "",
):
    query = get_select_query(table, properties, criteria, order_by)
    return await exec(query, fetch=True, params_seq=values)


def get_select_query(
    table: str, properties: list[str], criteria: str = "", order_by: str = ""
):
    query = f"""
        SELECT
            {', '.join(properties)}
        FROM
            chat.{table}
        {f'WHERE {criteria}' if criteria else ''}
        {f'ORDER BY {order_by}' if order_by else ''}
    """
    return wrap_query_as_json(query)


async def insert(
    table: str,
    items: list[BaseModel] | list[dict[Any, Any]],
    return_results: bool = False,
):
    dict_items = items_to_dicts(items)
    columns = items_to_columns(dict_items)
    query = get_insert_query(table, columns, return_results)
    values = items_to_values(dict_items)
    return await exec(query, values, auto_commit=True, fetch=return_results)


def items_to_dicts(items: list[BaseModel] | list[dict[Any, Any]]):
    return [item.dict() if isinstance(item, BaseModel) else item for item in items]


def items_to_columns(items: list[dict[Any, Any]]):
    return list(items[0].keys())


def items_to_values(items: list[dict[Any, Any]]):
    return [tuple(item.values()) for item in items]


def get_insert_query(table: str, columns: list[str], return_results: bool):
    return f"""
        INSERT INTO
            chat.{table}
            ({', '.join(columns)})
        VALUES
            ({', '.join(['%s'] * len(columns))})
        {f'RETURNING to_jsonb({table}.*)' if return_results else ''}
    """


def wrap_query_as_json(query: str):
    return f"""
        SELECT
            jsonb_agg(results)
        FROM
            ({query}) results
    """
