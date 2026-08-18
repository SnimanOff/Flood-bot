from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database.repositories import CheckRepository, MoneyRequestRepository, UserRepository
from src.service.errors import AppError
from src.service.logger import log_app, log_tech


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any]) -> Any:
        async with self._session_factory() as session:
            users = UserRepository(session)
            data["session"] = session
            data["users"] = users
            data["money_requests"] = MoneyRequestRepository(session)
            data["checks"] = CheckRepository(session)

            log_tech.debug("session open")

            from_user = data.get("event_from_user")
            if from_user is not None:
                user, created = await users.get_or_create(from_user.id, from_user.username)
                data["user"] = user
                if created:
                    log_app.info("user created tg_id={}", from_user.id)
                else:
                    log_tech.debug("user loaded tg_id={}", from_user.id)
            else:
                data["user"] = None

            try:
                result = await handler(event, data)
                await session.commit()
                log_tech.debug("session commit")
                return result
            except AppError as e:
                await session.rollback()
                log_app.warning("domain error: {}", e)
                raise
            except Exception:
                await session.rollback()
                log_app.exception("handler failed, rollback")
                raise
