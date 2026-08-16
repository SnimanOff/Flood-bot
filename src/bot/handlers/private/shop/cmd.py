from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.bot.handlers.private.shop.keyboard import kb_shop
from src.database.models import User
from src.service.vault.goods import get_goods

router = Router(name="shop")


# ---------------- магазин ----------------

@router.callback_query(F.data.startswith("shop_noop:"), F.message.chat.type == "private")
async def clbck_shop_noop(callback: CallbackQuery, user: User):
    parts = callback.data.split(":")
    cur, total = parts[1], parts[2]

    await callback.answer(f"Страница {cur} из {total}")

@router.callback_query(F.data.startswith("shop_page:"), F.message.chat.type == "private")
async def clbck_shop_page(callback: CallbackQuery, user: User):
    page = int(callback.data.split(":")[1])

    await callback.message.edit_reply_markup(reply_markup=kb_shop(get_goods(), page))
    await callback.answer()

@router.callback_query(F.data == "shop_select:purge_immunity", F.message.chat.type == "private")
async def clbck_shop_purge_immunity(callback: CallbackQuery, user: User):
    ...
