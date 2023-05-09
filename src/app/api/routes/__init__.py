from fastapi import APIRouter

from app.database.repositories.users import endpoints as userEndpoints

router = APIRouter()

router.include_router(userEndpoints.router)
