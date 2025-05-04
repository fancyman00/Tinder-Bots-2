from app.bot.api.service import BotServiceRouter
from app.tinder.database.models.bot import TinderBot
from bot.schemas.auth import OtpConfirm
from bot.api.auth import BotAuthRouter
from base.api.crud import CRUDRouter
from tinder.dependencies import get_bot_service, get_crud, get_auth_service
from fastapi import APIRouter
# from thaifriendly.api.messages import messages_router
from tinder.api.file import file_router
tinder_router = APIRouter()

bot_crud_router = CRUDRouter(TinderBot, "/bot/Tinder", ["Bot Tinder"], "Bot Tinder", get_crud)
bot_auth_router = BotAuthRouter("/bot/Tinder", ["Bot Tinder"], OtpConfirm, get_auth_service)
bot_service_router = BotServiceRouter("/bot/Tinder", ["Bot Tinder"], get_bot_service)
tinder_router.include_router(bot_crud_router)
tinder_router.include_router(file_router)
tinder_router.include_router(bot_auth_router)
tinder_router.include_router(bot_service_router)
# thaifriendly_router.include_router(bot_service_router)
# thaifriendly_router.include_router(messages_router)