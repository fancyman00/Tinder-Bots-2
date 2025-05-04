import json
from typing import List
from redis import asyncio as aioredis
from app.config import settings


class Session:
    def __init__(self, identity: str, params: List[str]):
        self.identity = identity
        self.params = params
        self.redis = aioredis.Redis(
            host=settings.REDIS.HOST,
            port=settings.REDIS.PORT,
            username=settings.REDIS.USER,
            password=settings.REDIS.PASS,
            db=settings.THAIFRIENDLY.COOKIES_REDIS_DB,
            socket_timeout=5,
        )

        self._session_keys = {value: f"{identity}:{value}" for value in self.params}
        self.session_data = {value: None for value in self.params}

    def __getitem__(self, key):    
        return self.session_data.get(key, None)

    def __setitem__(self, index, value):
        self.session_data[index] = value

    def get(self, key):    
        return self.__getitem__(key)

    def update(self, data: dict):
        for key, value in data.values():
            if key not in self.params:
                raise Exception(f"Undefined key {key}")
            self.session_data[key] = value

    async def load(self) -> bool:
        try:
            for param in self.params:
                if val := await self.redis.get(self._session_keys[param]):
                    self.session_data[param] = json.loads(val.decode())
        except Exception as e:
            raise e

    async def save(self) -> None:
        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                for param in self.params:
                    pipe.set(self._session_keys[param], json.dumps(self.session_data[param])) 
                await pipe.execute()
        except Exception as e:
            raise e

    async def clear(self) -> None:
        try:
            self.session_data = {value: None for value in self.params}
            async with self.redis.pipeline(transaction=True) as pipe:
                for param in self.params:
                    pipe.delete(self._session_keys[param])
                await pipe.execute()
        except Exception as e:
            raise e