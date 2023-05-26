import fastapi
from pydantic import error_wrappers
from app.database import databaseFuncs


def raise_model_exception(exception: error_wrappers.ValidationError):
    status_code = fastapi.status.HTTP_400_BAD_REQUEST
    if exception.raw_errors[0].exc.args:
        detail = exception.raw_errors[0].exc.args[0]
    else:
        detail = (
            f"{exception.raw_errors[0]._loc}, "
            f"{exception.raw_errors[0].exc.msg_template.replace('{limit_value}', str(exception.raw_errors[0].exc.limit_value))}"
        )
    databaseFuncs.raise_http_exception(status_code, detail)
