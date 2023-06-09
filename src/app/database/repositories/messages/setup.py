from app.database.repositories.messages import ITEM_TYPE
from app.database.connection import baseQueries


PROPERTIES = [
    "source_user_id bigint NOT NULL",
    "target_user_id bigint NOT NULL",
    "content text NOT NULL",
]
TABLE_QUERY = baseQueries.create_table_query(ITEM_TYPE, PROPERTIES)
