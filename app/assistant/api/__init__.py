from assistant.dependencies import get_assistant_crud
from assistant.database.models.assistant import Assistant
from base.api.crud import CRUDRouter
from fastapi import APIRouter

assistant_router = APIRouter()

assistant_crud_router = CRUDRouter(
    Assistant,
    "/assistant",
    ["Assistant"],
    "Assistant",
    get_assistant_crud,
)
assistant_router.include_router(assistant_crud_router)
