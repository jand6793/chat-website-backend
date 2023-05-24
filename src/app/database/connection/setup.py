import sys
from pathlib import Path

sys.path.append(str(Path.cwd() / "src"))
from app.database.connection.database import (
    open_backend_pool,
    postgres_exec,
    POSTGRES_CHAT_DATA_DSN,
)
from app.database.connection import baseQueries
from app.database.repositories.users import setup as usersSetup
from app.database.repositories.messages import setup as messagesSetup


def setup():
    open_backend_pool()

    backend_user = postgres_exec(
        baseQueries.create_backend_user_query(), auto_commit=True
    )
    if backend_user.error:
        print(backend_user.error)

    backend_db = postgres_exec(
        baseQueries.create_backend_database_query(), auto_commit=True
    )
    if backend_db.error:
        print(backend_db.error)

    chat_data_schema = postgres_exec(
        baseQueries.create_schema_query(), auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    if chat_data_schema.error:
        print(chat_data_schema.error)

    users_table = postgres_exec(
        usersSetup.TABLE_QUERY, auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    if users_table.error:
        print(users_table.error)

    messages_table = postgres_exec(
        messagesSetup.TABLE_QUERY, auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    if messages_table.error:
        print(messages_table.error)
    None


if __name__ == "__main__":
    setup()
