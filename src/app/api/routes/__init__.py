from fastapi import APIRouter

from app.database.repositories.users import endpoints as userEndpoints
from app.database.repositories.messages import endpoints as messageEndpoints
from app.database.repositories.conversations import endpoints as conversationEndpoints
from app.database.repositories.home import endpoints as homeEndpoints
from app.database.repositories.authentication import endpoints as authenticationEndpoints


router = APIRouter()

router.include_router(authenticationEndpoints.router)
router.include_router(userEndpoints.router)
router.include_router(messageEndpoints.router)
router.include_router(conversationEndpoints.router)
router.include_router(homeEndpoints.router)
