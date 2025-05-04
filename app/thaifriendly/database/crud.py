from thaifriendly.database.dao import ThaifriendlyBotDAO
from bot.database.crud import BotCRUD
from app.thaifriendly.database.models.bot import ThaifriendlyBot

class ThaifrinedlyBotCRUD(BotCRUD[ThaifriendlyBot, ThaifriendlyBotDAO]):
    def __init__(self):
        super().__init__(ThaifriendlyBotDAO())