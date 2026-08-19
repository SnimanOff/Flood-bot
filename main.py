import asyncio

from src.bot.main import start_bot
from src.database.core import close_db, init_db
from src.service.logger import log_app
from src.service.vault.version import refresh_version


async def main() -> None:
    await refresh_version()
    try:
        await start_bot()
    except Exception:
        log_app.exception("main failed")
        raise
    finally:
        await close_db()
        log_app.info("database closed")


if __name__ == "__main__":
    try:
        log_app.info("app starting")
        init_db()
        log_app.info("database ready / migrations done")
        asyncio.run(main())
    except Exception:
        log_app.exception("process exited with error")
        raise
