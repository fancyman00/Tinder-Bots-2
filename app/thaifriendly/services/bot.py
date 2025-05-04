from typing import List
from loguru import logger
from app.bot.services.auth import AuthService
from app.bot.services.bot import BotService
from app.storage.dependencies import get_storage
from app.thaifriendly.database.crud import ThaifrinedlyBotCRUD
from app.thaifriendly.database.models.bot import ThaifriendlyBot
from app.thaifriendly.infrastructure.automation import ThaiFriendlyAutomation


class ThaifriendlyBotService(BotService):
    def __init__(self, auth_service: AuthService, crud: ThaifrinedlyBotCRUD):
        super().__init__(auth_service, crud)
        self.auth_service = auth_service
        self.crud = crud

    async def _create_automation(self, bot_id: int) -> ThaiFriendlyAutomation:
        bot: ThaifriendlyBot = await self.crud.is_exist(bot_id)

        storage = await get_storage()
        api_key = await storage.get_setting("openaikey")
        assistant_id = bot.assistant.assistant_id or await storage.get_setting(
            "assistantid"
        )
        if not assistant_id:
            raise Exception("Assistant ID not found")
        if not api_key:
            raise Exception("API KEY not found")

        automation = ThaiFriendlyAutomation(
            bot_id=bot_id,
            api_key=api_key,
            asisstant_id=assistant_id,
            callback=lambda bid: self._handle_automation_stop(bid),
            redis=self.redis
        )

        return automation