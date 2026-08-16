from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.bot.handlers.private.shop.keyboard import kb_shop
from src.database.repositories import UserRepository
from src.service.vault.goods import get_goods

router = Router(name="shop")


# ---------------- магазин ----------------

@router.callback_query(F.data.startswith("shop_noop:"), F.message.chat.type == "private")
async def clbck_shop_noop(callback: CallbackQuery, users: UserRepository):
    await users.get_or_create(callback.from_user.id, callback.from_user.username)

    parts = callback.data.split(":")
    cur, total = parts[1], parts[2]

    await callback.answer(f"Страница {cur} из {total}")

@router.callback_query(F.data.startswith("shop_page:"), F.message.chat.type == "private")
async def clbck_shop_page(callback: CallbackQuery, users: UserRepository):
    await users.get_or_create(callback.from_user.id, callback.from_user.username)

    page = int(callback.data.split(":")[1])

    await callback.message.edit_reply_markup(reply_markup=kb_shop(get_goods(), page))
    await callback.answer()

@router.callback_query(F.data == "shop_select:purge_immunity", F.message.chat.type == "private")
async def clbck_shop_purge_immunity(callback: CallbackQuery, users: UserRepository):
    ...
