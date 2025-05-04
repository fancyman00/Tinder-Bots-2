from assistant.database.crud import AssistantCRUD


assistant_crud = AssistantCRUD()

async def get_assistant_crud():
    return assistant_crud