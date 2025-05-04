from app.tinder.database.models.bot import TinderBot
from app.bot.database.dao import BotDAO

class TinderBotDAO(BotDAO):
    model = TinderBot
    platform = 'Tinder'