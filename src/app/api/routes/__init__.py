from fastapi import APIRouter

from app.database.repositories.users import endpoints as userEndpoints
from app.database.repositories.messages import endpoints as messageEndpoints


router = APIRouter()

router.include_router(userEndpoints.router)
router.include_router(messageEndpoints.router)
