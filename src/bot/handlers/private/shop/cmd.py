from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.handlers.private.shop.keyboard import kb_buy, kb_shop
from src.database.models import User
from src.service.logger import log_app
from src.service.sendmsg import send_msg
from src.service.vault.goods import get_good, get_goods
from src.service.vault.texts import SHOP_TITLE, SHOP_UNAVAILABLE, txt_good_card, txt_page

router = Router(name="shop")


async def show_good_card(callback: CallbackQuery, good: dict) -> None:
    await send_msg(callback.message, txt_good_card(good), media=good.get("media") or "", reply_markup=kb_buy(str(good["id"])), edit=True)


@router.callback_query(F.data.startswith("shop_noop:"), F.message.chat.type == "private")
async def clbck_shop_noop(callback: CallbackQuery, user: User):
    parts = callback.data.split(":")
    cur, total = parts[1], parts[2]
    await callback.answer(txt_page(cur, total))


@router.callback_query(F.data.startswith("shop_page:"), F.message.chat.type == "private")
async def clbck_shop_page(callback: CallbackQuery, user: User):
    page = int(callback.data.split(":")[1])
    log_app.info("shop_page tg_id={} page={}", callback.from_user.id, page)
    await send_msg(callback.message, SHOP_TITLE, reply_markup=kb_shop(get_goods(), page), edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("shop_select:"), F.message.chat.type == "private")
async def clbck_shop_select(callback: CallbackQuery, user: User):
    good_id = callback.data.split(":", 1)[1]
    log_app.info("shop_select tg_id={} good_id={}", callback.from_user.id, good_id)
    good = get_good(good_id)

    if not good or not good.get("active", True):
        log_app.warning("shop unavailable tg_id={} good_id={}", callback.from_user.id, good_id)
        await callback.answer(SHOP_UNAVAILABLE, show_alert=True)
        return

    await show_good_card(callback, good)
    await callback.answer()
