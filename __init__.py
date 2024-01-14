from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.dependencies import get_db


def create_app() -> FastAPI:
    app = FastAPI(title=settings.API_NAME, description=settings.DESCRIPTION)

    origins = [
        "*"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from api.routes.v1.api import api_router
    app.include_router(api_router)

    @app.get("/healthcheck", tags=['devops'])
    async def get_healthcheck():
        return {"status": "ok"}

    return app
