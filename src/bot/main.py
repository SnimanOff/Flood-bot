import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from src.bot.handlers import setup_routers
from src.bot.middlewares import DbSessionMiddleware
from src.bot.middlewares.throttling import ThrottleMiddleware
from src.database.core import async_session_factory
from src.service.logger import log_app
from src.service.settings import settings


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware(async_session_factory))
    dp.message.middleware(ThrottleMiddleware())
    dp.include_router(setup_routers())
    return dp


async def start_bot() -> None:
    bot = Bot(token=settings.bot)
    dp = build_dispatcher()

    mode = (settings.bot_mode or "webhook").lower()
    if mode == "polling":
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            log_app.info("webhook cleared, polling mode")
            await dp.start_polling(bot)
        except Exception:
            log_app.exception("bot polling crashed")
            raise
        finally:
            await bot.session.close()
            log_app.info("bot stopped")
        return

    if not settings.webhook_host:
        raise RuntimeError("WEBHOOK_HOST is required in webhook mode (e.g. https://bot.example.com)")

    webhook_url = f"{settings.webhook_host.rstrip('/')}{settings.webhook_path}"
    secret = settings.webhook_secret or None

    async def on_startup() -> None:
        await bot.set_webhook(url=webhook_url, secret_token=secret, drop_pending_updates=True)
        log_app.info("webhook set url={}", webhook_url)

    async def on_shutdown() -> None:
        await bot.delete_webhook()
        log_app.info("webhook deleted")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=secret).register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=settings.webhook_port)
    await site.start()
    log_app.info("webhook server listening 0.0.0.0:{}", settings.webhook_port)

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await bot.session.close()
        log_app.info("bot stopped")
