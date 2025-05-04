from base.api.crud import CRUDRouter
from fastapi import APIRouter

from shared.log.database.models.log import Log
from shared.log.dependencies import get_log_crud

log_router = APIRouter()

log_crud_router = CRUDRouter(
    Log,
    "/logs", 
    ["Logs"],
    "Logs",
    get_log_crud
)
log_router.include_router(log_crud_router)
