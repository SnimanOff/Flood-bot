from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import time

from src.service.logger import log_tech


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, rate: float = 0.5) -> None:
        self.rate = rate
        self._last: dict[int, float] = {}

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any]) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last.get(user.id, 0.0)
        if now - last < self.rate:
            log_tech.debug("throttle skip user_id={}", user.id)
            return

        self._last[user.id] = now
        return await handler(event, data)
