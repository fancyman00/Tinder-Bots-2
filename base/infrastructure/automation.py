from datetime import datetime
from typing import Awaitable, Callable, List
from redis import asyncio as aioredis
from base.infrastructure.openai import OpenAIAssistantHandler




class Automation:
    def __init__(self, bot_id: int, api_key: str, asisstant_id: str, redis: aioredis.Redis, callback: Callable[[int], Awaitable[None]]):
        self.id = bot_id
        self.bot_id = bot_id
        self._running = False
        self.last_activity = datetime.now()
        self.openai_handler = OpenAIAssistantHandler(api_key=api_key, redis=redis)
        self.assistant_id = asisstant_id
        self.tasks: List[Callable] = []
        self.callback = callback

    async def pre_start(self):
        pass

    async def save_session(self):
        pass