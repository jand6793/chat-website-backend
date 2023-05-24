from dataclasses import dataclass, field
from typing import Any, Iterable

from psycopg.abc import Params, Query
from psycopg.errors import Error, Warning
from psycopg_pool import ConnectionPool

from app.core.config import config


@dataclass
class ExecResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    error: Warning | Error | None = None

    def new(
        self, records: list[Any] | None = None, error: Warning | Error | None = None
    ):
        return ExecResult(records=records or [], error=error)


# DATABASE_URL = (
#     "postgresql://postgres:postgres@database-1.c0bxyt0aqyaa.us-east-2.rds.amazonaws.com"
# )
POSTGRES_POSTGRES_DSN = f"postgresql://postgres:{config.postgres_password.get_secret_value()}@localhost:5432/postgres"
POSTGRES_CHAT_DATA_DSN = f"postgresql://postgres:{config.postgres_password.get_secret_value()}@localhost:5432/chat_data"
BACKEND_DSN = f"postgresql://backend:{config.postgres_password.get_secret_value()}@localhost:5432/chat_data"


backend_pool = ConnectionPool(BACKEND_DSN, open=False, min_size=5, max_size=10)


def open_backend_pool():
    backend_pool.open()


def close_backend_pool():
    backend_pool.close()


def postgres_exec(
    query: Query,
    params_seq: Iterable[Params] | None = None,
    *,
    fetch: bool = False,
    auto_commit: bool = False,
    dsn: str = POSTGRES_POSTGRES_DSN,
):
    pool = ConnectionPool(dsn, min_size=5, max_size=10)
    return _exec(
        pool,
        query,
        params_seq,
        fetch=fetch,
        auto_commit=auto_commit,
    )


def backend_exec(
    query: Query,
    params_seq: Iterable[Params] | None = None,
    *,
    fetch: bool = False,
    auto_commit: bool = False,
):
    return _exec(
        backend_pool,
        query,
        params_seq,
        fetch=fetch,
        auto_commit=auto_commit,
    )


def _exec(
    pool: ConnectionPool,
    query: Query,
    params_seq: Iterable[Params] | None,
    *,
    fetch: bool,
    auto_commit: bool,
):
    parameters = list(params_seq) if params_seq else []
    with pool.connection() as conn:
        conn.autocommit = auto_commit
        with conn.cursor() as cur:
            try:
                if parameters:
                    cur.execute(query, parameters)
                else:
                    cur.execute(query)
            except Exception as e:
                return ExecResult(error=e)
            results = cur.fetchall() if fetch else []
    return ExecResult(format_results(results))


def format_results(results: list[Any]) -> list[dict[str, Any]]:
    if not (results and results[0][0]):
        return []
    elif isinstance(results[0], tuple):
        if isinstance(results[0][0], list):
            return results[0][0]
        else:
            return [r[0] for r in results]
    else:
        return [r[0][0] for r in results]
