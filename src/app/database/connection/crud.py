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


def wrap_query_as_json(query: str):
    return f"""
        SELECT
            jsonb_agg(results)
        FROM
            ({query}) results
    """


async def insert(
    table: str,
    item: BaseModel | dict[Any, Any],
    return_results: bool = False,
):
    item_dict = item_to_dict(item)
    columns = item_to_columns(item_dict)
    query = get_insert_query(table, columns, return_results)
    values = item_to_values(item_dict)
    return await exec(query, values, auto_commit=True, fetch=return_results)


def item_to_dict(item: BaseModel | dict[Any, Any]):
    return item.dict() if isinstance(item, BaseModel) else item


def item_to_columns(item: dict[Any, Any]):
    return list(item.keys())


def item_to_values(item: dict[Any, Any]):
    return tuple(item.values())


def get_insert_query(table: str, columns: list[str], return_results: bool):
    return f"""
        INSERT INTO
            chat.{table}
            ({', '.join(columns)})
        VALUES
            ({', '.join(['%s'] * len(columns))})
        {f'RETURNING to_jsonb({table}.*)' if return_results else ''}
    """


async def update(
    table: str,
    item_id: int,
    item: BaseModel | dict[Any, Any],
    return_results: bool = False,
):
    item_dict = item_to_dict(item)
    columns = item_to_columns(item_dict)
    criteria = f"id = {item_id}"
    query = get_update_query(
        table, columns, criteria=criteria, return_results=return_results
    )
    values = item_to_values(item_dict)
    return await exec(query, values, auto_commit=True, fetch=return_results)


def get_update_query(
    table: str, columns: list[str], criteria: str = "", return_results: bool = False
):
    return f"""
        UPDATE
            chat.{table}
        SET
            {', '.join([f'{column} = %s' for column in columns])}
        {f'WHERE {criteria}' if criteria else ''}
        {f'RETURNING to_jsonb({table}.*)' if return_results else ''}
    """
