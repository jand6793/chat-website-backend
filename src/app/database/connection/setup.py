import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path.cwd() / "src"))

from app.core.config import config
from app.database.connection.database import (
    open_backend_pool,
    postgres_exec,
    POSTGRES_CHAT_DATA_DSN,
)


async def setup():
    await open_backend_pool()
    backend_user = await postgres_exec(create_backend_user_query(), auto_commit=True)
    backend_db = await postgres_exec(create_backend_database_query(), auto_commit=True)
    chat_data_schema = await postgres_exec(
        create_schema_query(), auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    users_table = await postgres_exec(
        create_users_table_query(), auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    messages_table = await postgres_exec(
        create_messages_table_query(), auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )
    friends_table = await postgres_exec(
        create_friends_table_query(), auto_commit=True, dsn=POSTGRES_CHAT_DATA_DSN
    )

    None


def create_backend_user_query():
    return f"""
        CREATE USER backend WITH
            LOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            INHERIT
            NOREPLICATION
            CONNECTION LIMIT 100
            PASSWORD '{config.backend_password.get_secret_value()}'
    """


def create_backend_database_query():
    return """
        CREATE DATABASE chat_data
            WITH
            OWNER = backend
            ENCODING = 'UTF8'
            CONNECTION LIMIT = 100
    """


def create_schema_query():
    return """
        CREATE SCHEMA chat;
        GRANT USAGE ON SCHEMA chat TO backend
    """


def create_users_table_query():
    return f"""
        CREATE TABLE chat.users
        (
            {base_properties()}
            full_name text NOT NULL,
            username text UNIQUE NOT NULL,
            description text,
            hashed_password text NOT NULL
        );
        
        {grant_backend_permissions("users")}
    """


def create_messages_table_query():
    return f"""
        CREATE TABLE chat.messages (
            {base_properties()}
            source_id bigint NOT NULL,
            destination_id bigint NOT NULL,
            message text NOT NULL
        );
        
        {grant_backend_permissions("messages")}
    """


def create_friends_table_query():
    return f"""
        CREATE TABLE chat.friends (
            {base_properties()}
            user_id bigint NOT NULL,
            friend_id bigint NOT NULL
        );
        
        {grant_backend_permissions("friends")}
    """


def base_properties():
    return """
        id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
        created timestamp with time zone DEFAULT current_timestamp,
        last_modified timestamp with time zone DEFAULT current_timestamp,
        deleted boolean NOT NULL DEFAULT FALSE,
        PRIMARY KEY (id),
    """


def grant_backend_permissions(table: str):
    return f"GRANT SELECT, INSERT, UPDATE ON TABLE chat.{table} TO backend"


if __name__ == "__main__":
    asyncio.run(setup())
