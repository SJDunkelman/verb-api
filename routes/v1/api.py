from fastapi import APIRouter
from routes.v1.endpoints import chat, auth, workflow, events, node


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(node.router, prefix="/node", tags=["node"])
