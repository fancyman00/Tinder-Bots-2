from typing import Callable
from fastapi import APIRouter, Depends
from app.bot.services.bot import BotService


def BotServiceRouter[
    ServiceType: BotService,
](
    prefix: str,
    tag: str,
    service_depend: Callable[[], ServiceType]
):
    router = APIRouter(prefix=prefix, tags=[tag])


    @router.post("/start/{id}")
    async def start_bot(
        id: int,
        service: ServiceType = Depends(service_depend),
    ):
        return await service.start(id)
        
    @router.post("/start_all")
    async def start_all(
        service: ServiceType = Depends(service_depend),
    ):
        return await service.start_all()


    @router.post("/stop/{id}")
    async def stop_bot(id: int, service: ServiceType = Depends(service_depend)):
        return await service.stop(id)


    @router.post("/stop_all")
    async def stop_all(
        service: ServiceType = Depends(service_depend),
    ):
        return await service.stop_all()

    return router
