import datetime

from fastapi import security, status, APIRouter, HTTPException, Depends

from app.core.config import config
from app.database.repositories.users import models as userModels
from app.services import authentication as auth


router = APIRouter(prefix="/api/v1/token", tags=["authentication"])


@router.post("", response_model=userModels.Token)
def login_for_access_token(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
):
    if user := auth.authenticate_user(form_data.username, form_data.password):
        access_token_expires = datetime.timedelta(
            minutes=config.access_token_expire_minutes
        )
        access_token = auth.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
