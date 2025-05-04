from typing import List

import httpx
from pydantic import BaseModel

from base.infrastructure.session import Session



class Client[User: BaseModel, Message: BaseModel]:
    def __init__(self, use_default_client = True, proxy = None, *args, **kwargs):
        self.client: httpx.AsyncClient | None = None 
        self.use_default_client = use_default_client
        self.session = Session(*args, **kwargs)
        self.proxy = proxy or "ufWFFH:k1ekcg@170.246.55.195:9489"
        self.proxies = {
            "http": f"http://{self.proxy}",
            "https": f"http://{self.proxy}",
        }

    async def connect(self) -> None:
        """Создает клиент и загружает сессию (если требуется)."""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, read=20.0),
                limits=httpx.Limits(max_keepalive_connections=5),
            )
            await self.load_session()

    async def close(self) -> None:
        """Закрывает клиент и сохраняет сессию."""
        await self.save_session()
        if self.client and not self.client.is_closed:
            await self.client.aclose()
        self.client = None
    async def __aenter__(self):
        await self.load_session()
        if self.use_default_client:
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.save_session()
        await self.close()

    async def request_authorize(self) -> None:
        """Запрос авторизации"""
        pass

    async def confirm_authorize(self) -> None:
        """Подтверждение авторизации"""
        pass

    async def load_session(self) -> None:
        await self.session.load()

    async def save_session(self) -> None:
        await self.session.save()

    async def clear_session(self) -> None:
        await self.session.clear()
        
    async def get_users_for_interaction(self) -> List[User]:
        """Получение списка пользователей для взаимодействия"""
        pass

    async def send_like(self, username: str) -> bool:
        """Отправка лайка пользователю"""
        pass

    async def get_conversations(self, username: str):
        """Получение списка текущих диалогов"""
        pass

    async def get_matches(self) -> List[Message]:
        """Получение списка текущих диалогов"""
        pass

    async def send_message(self, username: str, message: str) -> bool:
        """Отправка сообщения пользователю"""
        pass
