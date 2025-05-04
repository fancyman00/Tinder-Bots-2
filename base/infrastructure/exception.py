import asyncio
from functools import wraps
from typing import Awaitable, Callable

from loguru import logger


class AutomationError(Exception):
    """Базовое исключение для ошибок автоматизации"""

def handle_automation_errors(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
    @wraps(func)
    async def wrapper(self: 'AutomationManager', *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.critical(f"Error in {func.__name__}: {str(e)}")
            raise AutomationError(f"Error in {func.__name__}") from e
    return wrapper