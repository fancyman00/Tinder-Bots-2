

from shared.log.database.crud import LogCRUD


log_crud = LogCRUD()

async def get_log_crud():
    return log_crud