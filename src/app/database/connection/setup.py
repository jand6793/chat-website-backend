import asyncio
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
from app.database.repositories.friends import setup as friendsSetup
from app.database.repositories.conversations import setup as conversationsSetup
from app.database.repositories.messages import setup as messagesSetup


async def setup():
    await open_backend_pool()
    backend_user = await postgres_exec(
        baseQueries.create_backend_user_query(), auto_commit=True
    )
    backend_db = await postgres_exec(
        baseQueries.create_backend_database_query(), auto_commit=True
    )
    chat_data_schema = await postgres_exec(
        baseQueries.create_schema_query(), auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    users_table = await postgres_exec(
        usersSetup.TABLE_QUERY, auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    friends_table = await postgres_exec(
        friendsSetup.TABLE_QUERY, auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    conversations_table = await postgres_exec(
        conversationsSetup.TABLE_QUERY, auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    messages_table = await postgres_exec(
        messagesSetup.TABLE_QUERY, auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    None


if __name__ == "__main__":
    asyncio.run(setup())
