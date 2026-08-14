from aiogram import Bot, Dispatcher

from src.service.logger import logger
from src.service.settings import settings


async def start_bot() -> None:
    
    bot = Bot(token=settings.bot)
    dp = Dispatcher()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("webhook cleared")
        logger.info("bot polling started")
        await dp.start_polling(bot)

    finally:
        await bot.session.close()
        logger.info("bot stopped")

