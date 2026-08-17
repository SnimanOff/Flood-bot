from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.bot.handlers.private.shop.keyboard import kb_shop, kb_buy
from src.database.models import User
from src.service.sendmsg import send_msg
from src.service.vault.goods import get_goods, get_good
from src.service.vault.texts import SHOP_UNAVAILABLE, txt_good_card, txt_shop_page


router = Router(name="shop")


async def show_good_card(callback: CallbackQuery, good: dict) -> None:
    await send_msg(callback.message, txt_good_card(good), media=good.get("media") or "", reply_markup=kb_buy(str(good["id"])), edit=True)


@router.callback_query(F.data.startswith("shop_noop:"), F.message.chat.type == "private")
async def clbck_shop_noop(callback: CallbackQuery, user: User):
    parts = callback.data.split(":")
    cur, total = parts[1], parts[2]

    await callback.answer(txt_shop_page(cur, total))


@router.callback_query(F.data.startswith("shop_page:"), F.message.chat.type == "private")
async def clbck_shop_page(callback: CallbackQuery, user: User):
    page = int(callback.data.split(":")[1])

    await callback.message.edit_reply_markup(reply_markup=kb_shop(get_goods(), page))
    await callback.answer()


@router.callback_query(F.data.startswith("shop_select:"), F.message.chat.type == "private")
async def clbck_shop_select(callback: CallbackQuery, user: User):
    good_id = callback.data.split(":", 1)[1]
    good = get_good(good_id)

    if not good or not good.get("active", True):
        await callback.answer(SHOP_UNAVAILABLE, show_alert=True)
        return
    
    await show_good_card(callback, good)
    await callback.answer()
