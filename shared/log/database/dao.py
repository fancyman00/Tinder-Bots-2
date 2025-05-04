from base.database.dao.base import BaseDAO
from shared.log.database.models.log import Log


class LogDAO(BaseDAO):
    model = Log
