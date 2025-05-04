from app.tinder.database.dao import TinderBotDAO
from app.tinder.database.models.bot import TinderBot
from app.bot.database.crud import BotCRUD

class TinderBotCRUD(BotCRUD[TinderBot, TinderBotDAO]):
    def __init__(self):
        super().__init__(TinderBotDAO())