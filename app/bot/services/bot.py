from typing import List
from loguru import logger

from app.storage.dependencies import get_storage
from base.infrastructure.automation import Automation
from bot.schemas.bot import ActivateBot
from bot.database.crud import BotCRUD
from bot.database.models.bot import Bot
from bot.services.auth import AuthService
from base.infrastructure.automation_manager import AutomationManager
from config import settings
from redis import asyncio as aioredis


class BotService[BotType: Bot, AuthServiceType: AuthService, CrudType: BotCRUD]:
    def __init__(
        self,
        auth_service: AuthServiceType,
        crud: CrudType,
    ):
        self.task_manager = AutomationManager()
        self.redis = aioredis.Redis(
            host=settings.REDIS.HOST,
            port=settings.REDIS.PORT,
            username=settings.REDIS.USER,
            password=settings.REDIS.PASS,
            db=settings.THAIFRIENDLY.COOKIES_REDIS_DB,
            socket_timeout=5,
        )
        self.auth_service = auth_service
        self.crud = crud

    async def set_active(self, bot_id, state=True):
        await self.crud.update(item_id=bot_id, data=ActivateBot(is_active=state))

    async def start(self, bot_id: int) -> None:
        try:
            automation = await self._create_automation(bot_id=bot_id)
            await self.task_manager.add_automation(automation=automation)
            await self.set_active(bot_id=bot_id, state=True)
            logger.success(f"Bot {bot_id} started")
        except Exception as e:
            logger.error(f"Failed to start bot {bot_id}: {e}")
            raise

    async def start_all(self):
        bots: List[BotType] = await self.crud.get_all()
        for bot in bots:
            await self.start(bot.id)

    async def stop_all(self):
        bots: List[BotType] = await self.crud.get_all()
        for bot in bots:
            await self.stop(bot.id)

    async def stop(self, bot_id: int) -> None:
        await self.crud.is_exist(bot_id)
        try:
            await self.task_manager.stop_automation(bot_id)
            await self.set_active(bot_id, state=False)
            logger.success(f"Bot {bot_id} stopped")
        except Exception as e:
            logger.error(f"Error stopping bot {bot_id}: {e}")
            raise
        
    async def load_started(self) -> None:
        active_bots: List[BotType] = await self.crud.get_active()
        for bot in active_bots:
            try:
                automation = await self._create_automation(bot_id=bot.id)
                await self.task_manager.add_automation(automation=automation)
                await self.set_active(bot_id=bot.id, state=True)
                logger.success(f"Bot {bot.id} started")
            except Exception as e:
                logger.error(f"Failed to restore bot {bot.id}: {e}")

    async def _handle_automation_stop(self, bot_id: int):
        try:
            await self.auth_service.request_authorize(bot_id=bot_id, state=False)
            await self.set_active(bot_id, state=False)
        except Exception as e:
            logger.error(f"Error in stop handler for bot {bot_id}: {e}")


    # Под каждого бота переопределение

    async def _create_automation(self, bot_id: int) -> Automation:
        pass
