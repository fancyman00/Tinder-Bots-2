from fastapi import APIRouter

from app.thaifriendly.infrastructure.client import ThaiFriendlyClient

messages_router = APIRouter(prefix="/messages", tags=["Manager"])

@messages_router.get("/{bot_id}/{match_id}/")
async def get_messages(
    bot_id: int,
    match_id: str
):
    async with ThaiFriendlyClient(bot_id) as client:
        return await client.get_conversations(match_id)