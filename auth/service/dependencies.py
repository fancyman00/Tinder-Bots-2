from service.auth import authenticate_user
from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from exceptions import TokenExpiredException, NoJwtException, NoUserIdException, ForbiddenException, TokenNoFound
from service.models import User
from base.database.dao.session_maker import SessionDep


def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        authorization_header = request.headers.get("authorization")
        token = authorization_header.split(" ")[1]
    if not token:
        raise TokenNoFound
    return token


async def get_current_user(token: str = Depends(get_token), session: AsyncSession = SessionDep):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except JWTError:
        raise NoJwtException

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise TokenExpiredException
    password = payload.get('password')
    username = payload.get('username')
    if not password or not username:
        raise NoUserIdException
    user = await authenticate_user(username, password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role_id in [3, 4]:
        return current_user
    else:
        return False