from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

sys.path.append(str(Path.cwd() / "src"))

from app.api import routes
from app.core.config import config
from app.database.connection import database


def get_application():
    app = FastAPI()
    app.add_event_handler("startup", database.open_backend_pool)
    app.add_event_handler("shutdown", database.close_backend_pool)

    app.include_router(routes.router)
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static", StaticFiles(directory=Path.cwd() / "frontend"), name="static")

    return app


app = get_application()

if __name__ == "__main__":
    uvicorn.run(app, host=config.ip_address, port=config.port)
