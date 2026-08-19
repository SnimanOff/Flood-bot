from aiogram import Router

from src.bot.handlers.private.start.cmd import router as start_router
from src.bot.handlers.private.shop.cmd import router as shop_router
from src.bot.handlers.private.balance.cmd import router as balance_router
from src.bot.handlers.private.inventory.cmd import router as inventory_router
from src.bot.handlers.private.admin.cmd import router as admin_router
from src.bot.handlers.public.gm.cmd import router as gm_router
from src.bot.handlers.public.inline.cmd import router as inline_menu_router
from src.bot.handlers.public.rests.cmd import router as rests_router
from src.bot.handlers.public.unpurge.cmd import router as unpurge_router
from src.bot.handlers.public.help.cmd import router as help_router
from src.bot.handlers.goods.rest import router as rest_router
from src.bot.handlers.goods.purge_immunity import router as purge_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(rest_router)
    root.include_router(purge_router)
    root.include_router(shop_router)
    root.include_router(balance_router)
    root.include_router(inventory_router)
    root.include_router(admin_router)
    root.include_router(gm_router)
    root.include_router(inline_menu_router)
    root.include_router(rests_router)
    root.include_router(unpurge_router)
    root.include_router(help_router)
    return root
