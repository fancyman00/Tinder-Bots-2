from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from base.database.dao.base import BaseDAO
from base.database.dao.session_maker import session_manager


class BaseCRUD[ModelType]:
    def __init__(self, dao: BaseDAO[ModelType]):
        self.dao = dao

    @session_manager.connection(isolation_level="SERIALIZABLE", commit=False)
    async def get(self, id: int, session: AsyncSession) -> ModelType | None:
        return await self.dao.find_one_or_none(filters={"id": id}, session=session)

    @session_manager.connection(isolation_level="SERIALIZABLE", commit=False)
    async def get_all(self, session: AsyncSession, limit: int = None, page: int = None) -> List[ModelType]:
        if limit and page:
            return await self.dao.paginate(session=session, page=page, page_size=limit)
        else:
            return await self.dao.find_all(session=session)

    @session_manager.connection(isolation_level="SERIALIZABLE", commit=True)
    async def add(self, data: BaseModel, session: AsyncSession) -> ModelType:
        return await self.dao.add(values=data, session=session)

    @session_manager.connection(commit=True)
    async def update(
        self, item_id: int, data: BaseModel, session: AsyncSession
    ) -> int:
        return await self.dao.update(filters={"id": item_id}, values=data, session=session)

    @session_manager.connection(isolation_level="SERIALIZABLE", commit=True)
    async def delete(self, id: int, session: AsyncSession) -> bool:
        return await self.dao.delete(filters={"id": id}, session=session)
    
