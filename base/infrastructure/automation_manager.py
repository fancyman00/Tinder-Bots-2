from functools import partial
from typing import Dict
from asyncio import Lock, Task, get_event_loop
import asyncio
from loguru import logger

from base.infrastructure.automation import Automation
from base.infrastructure.exception import handle_automation_errors

class AutomationError(Exception):
    """Базовое исключение для ошибок автоматизации"""

class AutomationManager[AutomationType: Automation]:
    def __init__(self):
        self.task_groups: Dict[int, list[Task]] = {}
        self.automations: Dict[int, AutomationType] = {}
        self._lock = Lock()
        self.loop = get_event_loop()

    def _handle_task_done(self, bot_id: int, task: asyncio.Task):
        try:
            if task.exception():
                logger.error(f"Task failed for bot {bot_id}: {task.exception()}")
                asyncio.create_task(self._async_stop_handler(bot_id))
        except asyncio.CancelledError:
            pass

    async def _async_stop_handler(self, bot_id: int) -> None:
        if callback := self.automations.get(bot_id).callback:
            await callback(bot_id)
        await self.stop_automation(bot_id)

    @handle_automation_errors
    async def add_automation(self, automation: Automation) -> None:
        if not isinstance(automation, Automation):
            raise TypeError("Expected Automation instance")

        async with self._lock:
            if automation.id in self.automations:
                raise ValueError(f"Automation {automation.id} already exists")

            try:
                await automation.pre_start()
            except Exception as e:
                logger.error(str(e))
                if callback := automation.callback:
                    await callback(automation.id)
                raise AutomationError("Pre-start failed")
        try:
            async with self._lock:
                tasks = []
                for task_func in automation.tasks:
                    task = asyncio.create_task(task_func())
                    task.add_done_callback(partial(self._handle_task_done, automation.bot_id))
                    tasks.append(task)
                self.task_groups[automation.id] = tasks
                self.automations[automation.id] = automation
            logger.success(f"Automation {automation.id} started with {len(tasks)} tasks")
        except* Exception as eg:
            logger.error(f"Tasks failed for automation {automation.id}: {eg}")
            await self._async_stop_handler(automation.id)
            raise

    @handle_automation_errors
    async def stop_automation(self, bot_id: int) -> None:
        async with self._lock:
            if bot_id not in self.automations:
                return

            automation = self.automations.pop(bot_id, None)
            tg = self.task_groups.pop(bot_id, None)

        if not automation or not tg:
            return
        for task in tg:
            task.cancel()
        try:
            await automation.save_session()
            logger.success(f"Automation {bot_id} stopped successfully")
        except Exception as e:
            logger.error(f"Session save failed for bot {bot_id}: {str(e)}")
            raise

    @handle_automation_errors
    async def close_all(self) -> None:
        async with self._lock:
            bots = list(self.automations.keys())
        
        await asyncio.gather(*[
            self.stop_automation(bot_id)
            for bot_id in bots
        ], return_exceptions=True)
