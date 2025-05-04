from shared.log.database.dao import LogDAO
from shared.log.database.models.log import Log
from base.database.crud import BaseCRUD


class LogCRUD(BaseCRUD[Log]):
    def __init__(self):
        super().__init__(LogDAO())