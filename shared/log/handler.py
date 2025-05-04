import asyncio
from loguru import logger
from functools import partial

from base.database.dao.session_maker import session_manager
from shared.log.dependencies import get_log_crud
from shared.log.schemas.log import LogCreate

class AsyncDatabaseHandler:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        self.task = self.loop.create_task(self._process_queue())

    async def _process_queue(self):
        log_crud = await get_log_crud()
        while True:
            record = await self.queue.get()
            try:
                log_entry = LogCreate(
                    level=record["level"].name,
                    message=record["message"],
                    module=record["module"],
                    func_name=record["function"],
                    line_no=record["line"],
                    exception=record["exception"]
                )
                await log_crud.add(data=log_entry)
            except Exception as e:
                print(f"Log save error: {e}")
            await asyncio.sleep(0.1)

    def write(self, message):
        record = message.record
        self.loop.call_soon_threadsafe(
            partial(self.queue.put_nowait, {
                "level": record["level"],
                "message": record["message"],
                "module": record["module"],
                "function": record["function"],
                "line": record["line"],
                "exception": record["exception"] if "exception" in record else None
            })
        )

    async def stop(self):
        await self.queue.join()
        self.task.cancel()

# Инициализация в setup_logger
async def setup_logger():
    handler = AsyncDatabaseHandler(session_manager)
    
    logger.remove()
    logger.add(
        handler,
        format="{time} - {level} - {message}",
        level="DEBUG",
        enqueue=True,  # Критически важный параметр
        catch=True,
        backtrace=True,
        diagnose=True
    )
    
    return handler