from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter(tags=["home"])


@router.get("/")
def read_root():
    return RedirectResponse(url="/home/page.html")
