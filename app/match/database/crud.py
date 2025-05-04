from typing import List
from match.database.dao import MatchDAO
from match.database.models.match import Match
from base.database.crud import BaseCRUD
from base.database.dao.session_maker import session_manager
from sqlalchemy.ext.asyncio import AsyncSession

class MatchCRUD(BaseCRUD[Match]):
    def __init__(self):
        super().__init__(MatchDAO())

    @session_manager.connection(isolation_level="SERIALIZABLE", commit=False)
    async def get_bot_match(self, match_id: str, session: AsyncSession) -> List[Match]:
        return await self.dao.find_one_or_none(filters={"name": match_id}, session=session)