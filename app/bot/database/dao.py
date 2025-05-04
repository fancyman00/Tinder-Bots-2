from loguru import logger
from pydantic import BaseModel
from bot.database.models.bot import Bot
from base.database.dao.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, select
from sqlalchemy.exc import SQLAlchemyError

class BotDAO(BaseDAO):
    model = Bot
    platform = 'Bot'
    @classmethod
    async def update(cls, session: AsyncSession, filters: dict, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        bot_id = filters.get("id")

        if not bot_id:
            raise ValueError("Фильтр должен содержать 'id' для обновления")

        bot_fields = {k: v for k, v in values_dict.items() if hasattr(Bot, k)}
        child_fields = {k: v for k, v in values_dict.items() if hasattr(cls.model, k)}
        child_fields = {k: v for k, v in child_fields.items() if k not in bot_fields}
        try:
            if bot_fields:
                bot_query = (
                    sqlalchemy_update(Bot)
                    .where(Bot.id == int(bot_id))
                    .values(**bot_fields))
                await session.execute(bot_query)

            if child_fields:
                thai_query = (
                    sqlalchemy_update(cls.model)
                        .where(cls.model.id == bot_id)
                        .values(**child_fields)
                )
                await session.execute(thai_query)

            await session.flush()
            return 1

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при обновлении: {e}")
            raise e
        
    @classmethod    
    async def find_all(cls, session: AsyncSession, filters: dict = None, order = None):
        try:
            query = select(Bot).filter_by(type=cls.platform)
            if filters is not None:
                query = query.filter_by(**filters)
            if order is not None:
                query = query.order_by(order)
            result = await session.execute(query)
            records = result.scalars().all()
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filters}: {e}")
            raise

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: dict):
        try:
            query = select(Bot).filter_by(**filters)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filters}: {e}")
            raise

    @classmethod
    async def delete(cls, session: AsyncSession, filters: dict):
        if not filters:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")

        query = sqlalchemy_delete(Bot).filter_by(**filters)
        try:
            result = await session.execute(query)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при удалении записей: {e}")
            raise e