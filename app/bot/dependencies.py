from base.infrastructure.client import Client
from bot.services.bot import BotService
from bot.services.auth import AuthService
from bot.database.crud import BotCRUD


bot_crud = BotCRUD()
bot_auth = AuthService(bot_crud, Client)
bot_service = BotService(bot_auth, bot_crud)

async def get_auth_service():
    return bot_auth


async def get_crud():
    return bot_crud


async def get_bot_service():
    return bot_service