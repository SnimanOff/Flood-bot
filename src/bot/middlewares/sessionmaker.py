from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database.repositories import MoneyRequestRepository, UserRepository


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any]) -> Any:
        async with self._session_factory() as session:
            users = UserRepository(session)
            data["session"] = session
            data["users"] = users
            data["money_requests"] = MoneyRequestRepository(session)

            from_user = data.get("event_from_user")
            if from_user is not None:
                user, created = await users.get_or_create(from_user.id, from_user.username)
                data["user"] = user
            else:
                data["user"] = None

            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
