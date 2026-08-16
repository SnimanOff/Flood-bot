from aiogram import Router

from src.bot.handlers.private.start.cmd import router as start_router
from src.bot.handlers.private.shop.cmd import router as shop_router
from src.bot.handlers.private.balance.cmd import router as balance_router
from src.bot.handlers.public.gm.cmd import router as gm_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(shop_router)
    root.include_router(balance_router)
    root.include_router(gm_router)
    return root
