from app.database.repositories import COMMON_PROPERTIES


ITEM_TYPE = "users"

BASE_PROPERTIES = COMMON_PROPERTIES + [
    "full_name",
    "username",
    "description",
]
