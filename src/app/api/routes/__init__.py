from fastapi import APIRouter

from app.database.repositories.users import endpoints as userEndpoints
from app.database.repositories.messages import endpoints as messageEndpoints
from app.database.repositories.conversations import endpoints as conversationEndpoints


router = APIRouter()

router.include_router(userEndpoints.router)
router.include_router(messageEndpoints.router)
router.include_router(conversationEndpoints.router)
