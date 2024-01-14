from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings


def create_app() -> FastAPI:
    api_app = FastAPI(title=settings.API_NAME, description=settings.DESCRIPTION)

    origins = [
        "*"
    ]
    api_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from routes.v1.api import api_router
    api_app.include_router(api_router)

    @api_app.get("/healthcheck", tags=['devops'])
    async def get_healthcheck():
        return {"status": "ok"}

    return api_app


app = create_app()
