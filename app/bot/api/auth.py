from app.bot.services.auth import AuthService
from fastapi import APIRouter, Depends
from typing import Callable, Type
from pydantic import BaseModel


def BotAuthRouter[
    CodeType: BaseModel,
    ServiceType: AuthService,
](
    prefix: str,
    tag: str,
    CodeSchema: Type[CodeType],
    service_depend: Callable[[], ServiceType],
):
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.post("/authorize/{id}")
    async def authorize(
        id: int,
        service: ServiceType = Depends(service_depend),
    ):
        return await service.request_authorize(id)

    @router.post("/authorize_cancel/{id}")
    async def authorize_cancel(
        id: int,
        service: ServiceType = Depends(service_depend),
    ):
        return await service.request_authorize(id, False)


    @router.post("/confirm/{id}")
    async def confirm(
        id: int,
        data: CodeSchema,
        service: ServiceType = Depends(service_depend),
    ):
        return await service.confirm_authorize(id, data)

    return router