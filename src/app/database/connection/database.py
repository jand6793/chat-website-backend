import asyncio
from dataclasses import dataclass, field
from typing import Any, Iterable

from psycopg.abc import Params, Query
from psycopg.errors import Error, Warning
from psycopg_pool import AsyncConnectionPool

from app.core.config import config


@dataclass
class ExecResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    error: Warning | Error | None = None

    def new(
        self, records: list[Any] | None = None, error: Warning | Error | None = None
    ):
        return ExecResult(records=records or [], error=error)


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# DATABASE_URL = (
#     "postgresql://postgres:postgres@database-1.c0bxyt0aqyaa.us-east-2.rds.amazonaws.com"
# )
POSTGRES_POSTGRES_DSN = f"postgresql://postgres:{config.postgres_password.get_secret_value()}@localhost:5432/postgres"
POSTGRES_CHAT_DATA_DSN = f"postgresql://postgres:{config.postgres_password.get_secret_value()}@localhost:5432/chat_data"
BACKEND_DSN = f"postgresql://backend:{config.postgres_password.get_secret_value()}@localhost:5432/chat_data"


backend_pool = AsyncConnectionPool(BACKEND_DSN, open=False, min_size=5, max_size=10)


async def open_backend_pool():
    await backend_pool.open()


async def close_backend_pool():
    await backend_pool.close()


async def postgres_exec(
    query: Query,
    params_seq: Iterable[Params] | None = None,
    *,
    fetch: bool = False,
    auto_commit: bool = False,
    dsn: str = POSTGRES_POSTGRES_DSN,
):
    pool = AsyncConnectionPool(dsn, min_size=5, max_size=10)
    return await _exec(
        pool,
        query,
        params_seq,
        fetch=fetch,
        auto_commit=auto_commit,
    )


async def backend_exec(
    query: Query,
    params_seq: Iterable[Params] | None = None,
    *,
    fetch: bool = False,
    auto_commit: bool = False,
):
    return await _exec(
        backend_pool,
        query,
        params_seq,
        fetch=fetch,
        auto_commit=auto_commit,
    )


async def _exec(
    pool: AsyncConnectionPool,
    query: Query,
    params_seq: Iterable[Params] | None,
    *,
    fetch: bool,
    auto_commit: bool,
):
    parameters = list(params_seq) if params_seq else []
    async with pool.connection() as conn:
        await conn.set_autocommit(auto_commit)
        async with conn.cursor() as cur:
            try:
                # if len(parameters) > 1:
                #     await cur.executemany(query, parameters, returning=fetch)
                if parameters:
                    await cur.execute(query, parameters)
                else:
                    await cur.execute(query)
            except Exception as e:
                return ExecResult(error=e)
            results = await cur.fetchall() if fetch else []
    return ExecResult(format_results(results))


def format_results(results: list[Any]) -> list[dict[str, Any]]:
    if not (results and results[0][0]):
        return []
    elif isinstance(results[0], tuple):
        if isinstance(results[0][0], list):
            return [r[0][0] for r in results]
        else:
            return [r[0] for r in results]
    else:
        return [r[0][0] for r in results]
