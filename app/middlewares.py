from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import aiohttp

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "/docs" in str(request.url) or "/openapi.json" in str(request.url):
            return await call_next(request)
        token = request.headers.get("Authorization")
        
        if token:
            token = token.split(" ")[1]
            auth_service_url = "http://localhost:8001/auth/me"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(auth_service_url, headers={"Authorization": f"Bearer {token}"}) as response:
                    if response.status != 200:
                        message = await response.read()
                        return Response(status_code=401, content=message)
        else:
            return Response(status_code=401, content="Invalid token or unauthorized access")
        
        response = await call_next(request)
        return response


class UniversalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            if isinstance(e, HTTPException):
                status_code = e.status_code
                detail = e.detail
            else:
                status_code = 400
                detail = str(e)
            
            return JSONResponse(
                status_code=status_code,
                content=detail
            )
