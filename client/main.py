from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import HTTPException

app = FastAPI()

app.mount("/", StaticFiles(directory="dist", html=True), name="static")

@app.exception_handler(404)
async def spa_404_handler(request: Request, exc: HTTPException):
    return FileResponse("dist/index.html")