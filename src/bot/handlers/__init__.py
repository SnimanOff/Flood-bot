from aiogram import Router

from src.bot.handlers.private.start.cmd import router as start_router
from src.bot.handlers.private.shop.cmd import router as shop_router
from src.bot.handlers.private.topup.cmd import router as topup_router
from src.bot.handlers.private.my_items.cmd import router as my_items_router
from src.bot.handlers.public.setrole.cmd import router as setrole_router
from src.bot.handlers.public.give_money.cmd import router as give_money_router
from src.bot.handlers.public.setrest.cmd import router as setrest_router
from src.bot.handlers.inline.menu import router as inline_menu_router
from src.bot.handlers.inline.rests import router as inline_rests_router
from src.bot.handlers.inline.help import router as inline_help_router
from src.bot.handlers.inline.unpurge import router as inline_unpurge_router
from src.bot.handlers.public.rests.cmd import router as rests_router
from src.bot.handlers.public.unpurge.cmd import router as unpurge_router
from src.bot.handlers.public.help.cmd import router as help_router
from src.bot.handlers.shop_buy.rest import router as rest_buy_router
from src.bot.handlers.shop_buy.purge_immunity import router as purge_buy_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(rest_buy_router)
    root.include_router(purge_buy_router)
    root.include_router(shop_router)
    root.include_router(topup_router)
    root.include_router(my_items_router)
    root.include_router(setrole_router)
    root.include_router(give_money_router)
    root.include_router(setrest_router)
    root.include_router(inline_menu_router)
    root.include_router(inline_rests_router)
    root.include_router(inline_help_router)
    root.include_router(inline_unpurge_router)
    root.include_router(rests_router)
    root.include_router(unpurge_router)
    root.include_router(help_router)
    return root
