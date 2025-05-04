from app.thaifriendly.services.bot import ThaifriendlyBotService
from bot.schemas.auth import OtpConfirm
from thaifriendly.database.crud import ThaifrinedlyBotCRUD
from app.thaifriendly.database.models.bot import ThaifriendlyBot
from thaifriendly.infrastructure.client import ThaiFriendlyClient
from bot.services.auth import AuthService


bot_crud = ThaifrinedlyBotCRUD()
bot_auth = AuthService[ThaifriendlyBot, OtpConfirm, ThaifrinedlyBotCRUD, ThaiFriendlyClient](bot_crud, ThaiFriendlyClient)
bot_service = ThaifriendlyBotService(bot_auth, bot_crud)

async def get_auth_service():
    return bot_auth


async def get_crud():
    return bot_crud


async def get_bot_service():
    return bot_service