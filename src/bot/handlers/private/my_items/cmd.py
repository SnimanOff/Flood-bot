from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.handlers.private.my_items.keyboard import kb_my_items
from src.database.models import User
from src.service.logger import log_app
from src.service.sendmsg import send_msg
from src.service.vault.goods import GOODS, get_good
from src.service.vault.texts import MY_ITEMS_INV_EMPTY, MY_ITEMS_REST_NONE, txt_my_items, txt_my_items_inventory_line, txt_my_items_rest_active

router = Router(name="my_items")


def build_my_items_text(user: User) -> str:
    inv = user.inventory or {}
    items = []

    for good_id, qty in inv.items():
        q = int(qty or 0)

        if q <= 0:
            continue

        good = get_good(str(good_id)) or GOODS.get(good_id)
        title = good["title"] if good else str(good_id)
        items.append((title, q))

    items.sort(key=lambda x: (-x[1], x[0].lower()))

    if items:
        inv_block = "\n".join(txt_my_items_inventory_line(t, q) for t, q in items)
    else:
        inv_block = MY_ITEMS_INV_EMPTY

    rest_until = user.rest_until
    today = datetime.now(timezone.utc).date()

    if rest_until is not None and rest_until >= today:
        rest_block = txt_my_items_rest_active(rest_until.strftime("%d.%m.%Y"))
    else:
        rest_block = MY_ITEMS_REST_NONE

    return txt_my_items(inv_block, rest_block)


@router.callback_query(F.data == "start_my_items", F.message.chat.type == "private")
async def clbck_my_items(callback: CallbackQuery, user: User):
    log_app.info("my_items tg_id={}", user.tg_id)
    text = build_my_items_text(user)
    await send_msg(callback.message, text, reply_markup=kb_my_items(), edit=True)
    await callback.answer()
