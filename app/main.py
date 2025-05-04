from pathlib import Path
import sys

project_root = Path(__file__).parent.parent 
sys.path.append(str(project_root))
from contextlib import asynccontextmanager
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from thaifriendly.dependencies import get_bot_service
from middlewares import AuthMiddleware, UniversalExceptionMiddleware
from fastapi import APIRouter, FastAPI

from assistant.api import assistant_router
from shared.log.api import log_router
from match.api import match_router
from storage.api import router as storage_router
from thaifriendly.api import thaifriendly_router
from tinder.api import tinder_router
from shared.log.handler import setup_logger
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI начал работу.")
    bot_service = await get_bot_service()
    await bot_service.load_started()
    handler = await setup_logger()
    yield
    await handler.stop()
    print("FastAPI завершил работу.")

def configure_api() -> APIRouter:
    api_v1_router = APIRouter(prefix='/v1')

    for api in [match_router, storage_router, assistant_router, log_router, thaifriendly_router, tinder_router]:
        api_v1_router.include_router(router=api)
    return api_v1_router

def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(UniversalExceptionMiddleware)
    app.include_router(configure_api())

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.logger = logger
    return app


uvicorn.run(app=get_app())
