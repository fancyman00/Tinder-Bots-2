from thaifriendly.database.models.bot import ThaifriendlyBot
from bot.api.service import BotServiceRouter
from bot.schemas.auth import OtpConfirm
from bot.api.auth import BotAuthRouter
from base.api.crud import CRUDRouter
from thaifriendly.dependencies import get_auth_service, get_bot_service, get_crud
from fastapi import APIRouter
from thaifriendly.api.messages import messages_router

thaifriendly_router = APIRouter()

bot_crud_router = CRUDRouter(ThaifriendlyBot, "/bot/Thaifriendly", ["Bot Thaifriendly"], "Bot Thaifriendly", get_crud)
bot_auth_router = BotAuthRouter("/bot/Thaifriendly", ["Bot Thaifriendly"], OtpConfirm, get_auth_service)
bot_service_router = BotServiceRouter("/bot/Thaifriendly", ["Bot Thaifriendly"], get_bot_service)
thaifriendly_router.include_router(bot_crud_router)
thaifriendly_router.include_router(bot_auth_router)
thaifriendly_router.include_router(bot_service_router)
thaifriendly_router.include_router(messages_router)