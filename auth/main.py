from pathlib import Path
import sys

project_root = Path(__file__).parent.parent  # Adjust based on your structure
sys.path.append(str(project_root))
import uvicorn
from service.router import router as router_auth
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI начал работу.")
    yield
    print("FastAPI завершил работу.")


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router_auth)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

# app = get_app()
uvicorn.run(app=get_app(), port=8001)
