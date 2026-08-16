from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import setup_routers
from src.bot.middlewares import DbSessionMiddleware
from src.bot.middlewares.throttling import ThrottleMiddleware
from src.database.core import async_session_factory
from src.service.logger import logger
from src.service.settings import settings


async def start_bot() -> None:
    bot = Bot(token=settings.bot)
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DbSessionMiddleware(async_session_factory))
    dp.message.middleware(ThrottleMiddleware())
    dp.include_router(setup_routers())

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("webhook cleared")
        await dp.start_polling(bot)
        logger.info("bot polling started")

    finally:
        await bot.session.close()
        logger.info("bot stopped")
