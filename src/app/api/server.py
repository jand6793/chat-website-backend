from pathlib import Path
import sys

import fastapi
import uvicorn

sys.path.append(str(Path.cwd() / "src"))

from app.api import routes
from app.core.config import config
from app.database.connection import database


def get_application():
    app = fastapi.FastAPI()
    app.add_event_handler("startup", database.open_backend_pool)
    app.add_event_handler("shutdown", database.close_backend_pool)
    app.include_router(routes.router)

    return app


app = get_application()

if __name__ == "__main__":
    uvicorn.run(app, host=config.ip_address, port=config.port)
