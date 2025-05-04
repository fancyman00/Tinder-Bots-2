import json
from typing import Any, Optional, Dict
import redis.asyncio as aioredis
from config import settings  # Импорт вашего модуля с настройками


class SettingsRedisStorage:
    def __init__(
        self,
        host: str = settings.REDIS.HOST,
        port: int = settings.REDIS.PORT,
        username: str = settings.REDIS.USER,
        password: str = settings.REDIS.PASS,
        db: int = 12,
        prefix: str = "settings:"
    ):
        self.redis = aioredis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            db=db,
            decode_responses=False  # Обрабатываем декодирование самостоятельно
        )
        self.prefix = prefix

    async def set_setting(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Сохранение настройки с возможным TTL (в секундах)"""
        full_key = self.prefix + key
        serialized = json.dumps(value)
        await self.redis.set(full_key, serialized, ex=ttl)

    async def get_setting(self, key: str) -> Any:
        """Получение настройки"""
        full_key = self.prefix + key
        serialized = await self.redis.get(full_key)
        if serialized is None:
            return None
        return json.loads(serialized)

    async def delete_setting(self, key: str) -> None:
        """Удаление настройки"""
        full_key = self.prefix + key
        await self.redis.delete(full_key)

    async def get_all_settings(self) -> Dict[str, Any]:
        """Получение всех настроек"""
        keys = []
        cursor = 0
        pattern = self.prefix + "*"

        while True:
            cursor, partial_keys = await self.redis.scan(cursor, match=pattern)
            keys.extend(partial_keys)
            if cursor == 0:
                break

        settings = {}
        for key in keys:
            value = await self.redis.get(key)
            setting_key = key.decode().replace(self.prefix, "", 1)
            settings[setting_key] = json.loads(value) if value else None

        return settings

    async def close(self) -> None:
        await self.redis.close()

    async def ping(self) -> bool:
        return await self.redis.ping()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
