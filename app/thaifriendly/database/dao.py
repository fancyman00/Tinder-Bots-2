from app.thaifriendly.database.models.bot import ThaifriendlyBot
from bot.database.dao import BotDAO

class ThaifriendlyBotDAO(BotDAO):
    model = ThaifriendlyBot
    platform = 'Thaifriendly'
