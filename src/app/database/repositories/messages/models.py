from typing import Self

import pydantic

from app.models import validatorFuncs, baseModels


class MessageCreate(pydantic.BaseModel):
    target_user_id: int
    content: str

    _validate_target_user_id = pydantic.validator("target_user_id", allow_reuse=True)(
        validatorFuncs.validate_64_bit_id
    )
    _validate_content = pydantic.validator("content", allow_reuse=True)(
        validatorFuncs.validate_string_passage
    )


class MessageToDB(MessageCreate):
    source_user_id: int

    _validate_source_user_id = pydantic.validator("source_user_id", allow_reuse=True)(
        validatorFuncs.validate_64_bit_id
    )


class MessageUpdate(pydantic.BaseModel):
    source_user_id: int | None = None
    target_user_id: int | None = None
    content: str | None = None

    @pydantic.root_validator()
    def validate_any_values_are_specified(
        cls: Self, values: dict[str, int | str | None]
    ):
        if not any(values.values()):
            raise ValueError("At least one property must be specified")
        else:
            return values

    _validate_first_name = pydantic.validator("source_user_id", allow_reuse=True)(
        validatorFuncs.validate_64_bit_id
    )
    _validate_last_name = pydantic.validator("target_user_id", allow_reuse=True)(
        validatorFuncs.validate_64_bit_id
    )
    _validate_username = pydantic.validator("content", allow_reuse=True)(
        validatorFuncs.validate_string_passage
    )


class MessageCriteria(
    baseModels.IdCriteria,
    baseModels.PaginationBaseProperties,
):
    source_user_id: int | None = None
    target_user_id: int | None = None
    content: str | None = None

    exclude_source_user_id: bool = False
    exclude_target_user_id: bool = False
    exclude_content: bool = False

    _validate_source_user_id = pydantic.validator("source_user_id", allow_reuse=True)(
        validatorFuncs.validate_64_bit_id
    )
    _validate_target_user_id = pydantic.validator("target_user_id", allow_reuse=True)(
        validatorFuncs.validate_64_bit_id
    )
    _validate_content = pydantic.validator("content", allow_reuse=True)(
        validatorFuncs.validate_string_passage
    )
