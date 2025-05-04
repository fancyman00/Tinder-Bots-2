from storage.service import SettingsRedisStorage


storage = SettingsRedisStorage()

async def get_storage():
    return storage
