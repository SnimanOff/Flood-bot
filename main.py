import asyncio

from src.bot.main import start_bot
from src.database.core import close_db, init_db
from src.service.logger import logger


async def main() -> None:
    await init_db()
    logger.info("database ready")
    try:
        await start_bot()
    finally:
        await close_db()
        logger.info("database closed")


if __name__ == "__main__":
    asyncio.run(main())
