from base.database.dao.session_maker import session_manager
from bot.exceptions import BotNotFound
from bot.database.models.bot import Bot
from bot.database.dao import BotDAO
from base.database.crud import BaseCRUD
from sqlalchemy.ext.asyncio import AsyncSession

class BotCRUD[BotType: Bot, DaoType: BotDAO](BaseCRUD[BotType]):
    def __init__(self, dao: DaoType = BotDAO):
        super().__init__(dao)
        self.BotType = type[BotType]

    async def is_exist(self, id: int):
        if bot := await super().get(id):
            return bot
        else:
            raise BotNotFound(id)
    
    @session_manager.connection(isolation_level="SERIALIZABLE", commit=False)
    async def get_active(self, session: AsyncSession):
        return await self.dao.find_all(session=session, filters={"is_active": True})
    