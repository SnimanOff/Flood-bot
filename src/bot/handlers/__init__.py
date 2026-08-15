from aiogram import Router

from src.bot.handlers.private.start.cmd import router as start_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    return root
