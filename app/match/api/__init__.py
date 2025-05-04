from match.database.models.match import Match
from match.dependencies import get_match_crud
from base.api.crud import CRUDRouter
from fastapi import APIRouter

match_router = APIRouter()

match_crud_router = CRUDRouter(
    Match,
    "/match",
    ["Match"],
    "Match",
    get_match_crud,
)
match_router.include_router(match_crud_router)
