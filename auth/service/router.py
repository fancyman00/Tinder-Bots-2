from typing import List
from fastapi import APIRouter, HTTPException, Response, Depends
from service.dependencies import get_current_user, get_current_admin_user
from service.models import User
from exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException
from service.auth import authenticate_user, create_access_token
from service.dao import UsersDAO
from service.schemas import (
    ChangePassword,
    SUserRegister,
    SUserAuth,
    EmailModel,
    SUserAddDB,
    SUserInfo,
    UpdateRole,
)
from sqlalchemy.ext.asyncio import AsyncSession

from base.database.dao.session_maker import TransactionSessionDep, SessionDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register/")
async def register_user(
    user_data: SUserRegister,
    session: AsyncSession = TransactionSessionDep,
    isAdmin: bool = Depends(get_current_admin_user),
) -> dict:
    if not isAdmin:
        return {"message": f"Вы не админ!"}
    user = await UsersDAO.find_one_or_none(
        session=session, filters={"username": user_data.username}
    )
    if user:
        raise UserAlreadyExistsException
    user_data_dict = user_data.model_dump()
    del user_data_dict["confirm_password"]
    await UsersDAO.add(session=session, values=SUserAddDB(**user_data_dict))
    return {"message": f"Успешно!"}


@router.post("/change_password/")
async def change_password(
    user_data: ChangePassword,
    session: AsyncSession = TransactionSessionDep,
    isAdmin: bool = Depends(get_current_admin_user),
) -> str:
    if not isAdmin:
        return {"message": f"Вы не админ!"}

    check: User = await authenticate_user(
        session=session, username=user_data.username, password=user_data.old_password
    )
    if check is None:
        raise IncorrectEmailOrPasswordException

    user_data_dict = user_data.model_dump()
    del user_data_dict["confirm_password"]
    del user_data_dict["old_password"]
    await UsersDAO.update(
        session=session,
        filters={"username": user_data.username},
        values=SUserAddDB(**user_data_dict),
    )
    return "Пароль успешно оновлен!"


@router.post("/login/")
async def auth_user(
    response: Response, user_data: SUserAuth, session: AsyncSession = SessionDep
):
    check: User = await authenticate_user(
        session=session, username=user_data.username, password=user_data.password
    )
    if check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(check.id), "role_id": check.role_id, "password": user_data.password, "username": user_data.username})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {
        "ok": True,
        "access_token": access_token,
        "message": "Авторизация успешна!",
        "role_id": check.role_id,
        "username": check.username,
    }


@router.post("/refresh/")
async def auth_user(
    response: Response,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = TransactionSessionDep,
):
    user_data = SUserInfo.model_validate(user_data)
    if not user_data:
        return {"ok": False, "access_token": access_token, "message": "Токен истек!"}
    check: User = await authenticate_user(
        session=session, username=user_data.username, password=user_data.password
    )
    if check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(check.id), "role_id": check.role_id})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {"ok": True, "access_token": access_token, "message": "Авторизация успешна!"}


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {"message": "Пользователь успешно вышел из системы"}


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserInfo:
    return SUserInfo.model_validate(user_data)


@router.get("/admin/")
async def is_admin(isAdmin: bool = Depends(get_current_admin_user)):
    if not isAdmin:
        raise HTTPException(status_code=401, detail="You is not admin")


@router.delete("/users/{id}")
async def delete_user(
    id: int,
    session: AsyncSession = SessionDep,
    admin: User = Depends(get_current_admin_user),
):
    if not admin:
        return {"message": f"Вы не админ!"}
    user: User = await UsersDAO.find_one_or_none_by_id(data_id=id, session=session)
    if admin.id == user.id:
        raise Exception("You can not do it with yourself.")

    if not user:
        raise Exception("Bot with id not found.")
    await UsersDAO.delete(session=session, filters={"id": id})
    await session.commit()


@router.get("/users/")
async def get_all_users(
    session: AsyncSession = SessionDep, isAdmin: bool = Depends(get_current_admin_user)
) -> List[SUserInfo]:
    if not isAdmin:
        return {"message": f"Вы не админ!"}
    return await UsersDAO.find_all(session=session)


@router.post("/access/{id}")
async def access(
    id: int,
    session: AsyncSession = TransactionSessionDep,
    admin: User = Depends(get_current_admin_user),
):
    if not admin:
        return {"message": f"Вы не админ!"}
    user: User = await UsersDAO.find_one_or_none_by_id(data_id=id, session=session)
    if admin.id == user.id:
        raise Exception("You can not do it with yourself.")

    if not user:
        raise Exception("Bot with id not found.")
    new_role = 3 if user.role_id == 1 else 1
    await UsersDAO.update(
        session=session, instance_id=id, values=UpdateRole(role_id=new_role)
    )
