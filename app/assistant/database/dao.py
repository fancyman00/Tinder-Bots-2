from assistant.database.models.assistant import Assistant
from base.database.dao.base import BaseDAO

class AssistantDAO(BaseDAO):
    model = Assistant