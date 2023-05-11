from app.database.repositories import COMMON_PROPERTIES


ITEM_TYPE = "messages"

BASE_PROPERTIES = COMMON_PROPERTIES + ["source_user_id", "target_user_id", "content"]
