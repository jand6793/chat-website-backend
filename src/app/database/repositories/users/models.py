import datetime
from typing import Self

import pydantic

from app.models import validatorFuncs, baseModels


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    username: str | None = None


class UserBase(pydantic.BaseModel):
    full_name: str
    username: str
    description: str | None = None

    _validate_first_name = pydantic.validator("full_name", allow_reuse=True)(
        validatorFuncs.validate_string_name
    )
    _validate_username = pydantic.validator("username", allow_reuse=True)(
        validatorFuncs.validate_string_name
    )
    _validate_description = pydantic.validator("description", allow_reuse=True)(
        validatorFuncs.validate_string_passage
    )


class User(UserBase, baseModels.IdDeleted):
    created: datetime.datetime
    last_modified: datetime.datetime


class UserInDB(User):
    hashed_password: str


class UserCreate(UserBase):
    password: str

    _validate_password = pydantic.validator("password", allow_reuse=True)(
        validatorFuncs.validate_string_name
    )


class UsersCreate(pydantic.BaseModel):
    users: tuple[UserCreate, ...]


class UserUpdate(pydantic.BaseModel):
    full_name: str | None = None
    password: str | None = None
    description: str | None = None

    @pydantic.root_validator()
    def validate_any_values_are_specified(cls: Self, values: dict[str, str | None]):
        if not any(values.values()):
            raise ValueError("At least one property must be specified")
        else:
            return values

    _validate_first_name = pydantic.validator("full_name", allow_reuse=True)(
        validatorFuncs.validate_string_name
    )
    _validate_password = pydantic.validator("password", allow_reuse=True)(
        validatorFuncs.validate_string_name
    )
    _validate_description = pydantic.validator("description", allow_reuse=True)(
        validatorFuncs.validate_string_passage
    )


class UserUpdateToDB(UserUpdate):
    hashed_password: str | None = None


class UserToDB(UserBase):
    hashed_password: str


class UserCriteria(
    baseModels.IdCriteria,
    baseModels.PaginationBaseProperties,
):
    full_name: str | None = None
    username: str | None = None
    description: str | None = None
    from_messages: bool | None = None

    exclude_full_name: bool = False
    exclude_username: bool = False
    exclude_description: bool = False

    _validate_full_name = pydantic.validator("full_name", allow_reuse=True)(
        validatorFuncs.validate_string_name
    )
    _validate_username = pydantic.validator("username", allow_reuse=True)(
        validatorFuncs.validate_string_name
    )
    _validate_description = pydantic.validator("description", allow_reuse=True)(
        validatorFuncs.validate_string_passage
    )
