from assistant.database.dao import AssistantDAO
from assistant.database.models.assistant import Assistant
from base.database.crud import BaseCRUD


class AssistantCRUD(BaseCRUD[Assistant]):
    def __init__(self):
        super().__init__(AssistantDAO())