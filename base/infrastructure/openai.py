import asyncio
from typing import Optional
import openai
import redis.asyncio as aioredis
from loguru import logger

class OpenAIAssistantHandler:
    def __init__(self, api_key: str, redis: aioredis.Redis):
        self.client = openai.AsyncClient(api_key=api_key)
        self.redis = redis

    async def create_thread(self) -> str:
        thread = await self.client.beta.threads.create()
        thread_id = thread.id
        return thread_id

    async def add_message(self, thread_id: str, content: str, role: str = "user") -> dict:
        message = await self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )
        return message

    async def run_assistant(self, assistant_id: str, thread_id: str, additional_instructions: str) -> dict:  
        run = await self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            additional_instructions=additional_instructions,
        )
                
        while run.status not in ["completed", "failed", "cancelled"]:
            logger.debug(f"Current run status: {run.status}. Waiting...")
            await asyncio.sleep(1)
            run = await self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
        
        if run.status == "failed":
            error_msg = f"Run {run.id} failed: {run.last_error}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        return run

    async def get_messages(self, thread_id: str) -> list:
        messages = await self.client.beta.threads.messages.list(thread_id=thread_id)
        sorted_messages = sorted(messages.data, key=lambda x: x.created_at)
        
        formatted_messages = []
        for msg in sorted_messages:
            for content in msg.content:
                if content.type == "text":
                    formatted_messages.append({
                        "role": msg.role,
                        "content": content.text.value,
                        "timestamp": msg.created_at
                    })
        return formatted_messages

    async def _get_thread_key(self, bot_id: int, username: str) -> str:
        key = f"bot:{bot_id}:user:{username}:thread"
        return key

    async def get_thread(self, bot_id: int, username: str) -> Optional[str]:
        key = await self._get_thread_key(bot_id, username)
        thread_id = await self.redis.get(key)
        if thread_id:
            thread_id = thread_id.decode()
            return thread_id
        return None

    async def save_thread(self, bot_id: int, username: str, thread_id: str):
        key = await self._get_thread_key(bot_id, username)
        await self.redis.set(key, thread_id)

    async def delete_thread(self, bot_id: int, username: str):
        key = await self._get_thread_key(bot_id, username)
        await self.redis.delete(key)
