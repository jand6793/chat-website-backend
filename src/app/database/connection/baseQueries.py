from app.core.config import config


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


def create_table_query(item_type: str, properties: list[str]):
    return f"""
        CREATE TABLE chat.{item_type}
        (
            {base_properties()}
            {', '.join(properties)}
        );
        
        {grant_backend_permissions(item_type)}
    """


def grant_backend_permissions(table: str):
    return f"GRANT SELECT, INSERT, UPDATE ON TABLE chat.{table} TO backend"


def base_properties():
    return """
        id bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
        created timestamp with time zone DEFAULT current_timestamp,
        last_modified timestamp with time zone DEFAULT current_timestamp,
        deleted boolean NOT NULL DEFAULT FALSE,
        PRIMARY KEY (id),
    """
