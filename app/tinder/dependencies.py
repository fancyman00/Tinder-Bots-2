from app.tinder.database.crud import TinderBotCRUD
from app.tinder.database.models.bot import TinderBot
from app.tinder.infrastructure.client import TinderClient
from app.tinder.services.bot import TinderBotService
from bot.schemas.auth import OtpConfirm
from thaifriendly.infrastructure.client import ThaiFriendlyClient
from bot.services.auth import AuthService


bot_crud = TinderBotCRUD()
bot_auth = AuthService[TinderBot, OtpConfirm, TinderBotCRUD, ThaiFriendlyClient](bot_crud, TinderClient)
bot_service = TinderBotService(bot_auth, bot_crud)

async def get_auth_service():
    return bot_auth


async def get_crud():
    return bot_crud


async def get_bot_service():
    return bot_service