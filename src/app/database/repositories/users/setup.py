from app.database.repositories.users import ITEM_TYPE
from app.database.connection import baseQueries


PROPERTIES = [
    "full_name text NOT NULL",
    "username text UNIQUE NOT NULL",
    "description text",
    "hashed_password text NOT NULL",
]
TABLE_QUERY = baseQueries.create_table_query(ITEM_TYPE, PROPERTIES)
