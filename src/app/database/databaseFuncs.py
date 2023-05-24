from fastapi import HTTPException


def raise_http_exception(status_code: int, detail: str | None):
    raise HTTPException(status_code=status_code, detail=detail)
