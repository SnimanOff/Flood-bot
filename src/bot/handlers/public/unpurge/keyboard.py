import math

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.service.vault.buttons import BTN_BACK, BTN_NEXT
from src.service.vault.texts import txt_unpurge_btn


PER_PAGE = 4


def kb_unpurge(holders: list, page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    total = max(1, math.ceil(len(holders) / PER_PAGE)) if holders else 1
    page = max(0, min(page, total - 1))
    chunk = holders[page * PER_PAGE : (page + 1) * PER_PAGE]

    for user, qty in chunk:
        label = txt_unpurge_btn(user.username, user.tg_id, qty)
        builder.button(text=label, callback_data=f"unpurge_take:{user.tg_id}", style="primary")
    builder.adjust(1)

    nav = []
    if total > 1:
        if page > 0:
            nav.append(InlineKeyboardButton(text=BTN_BACK, callback_data=f"unpurge_page:{page - 1}", style="primary"))
        nav.append(InlineKeyboardButton(text=f"{page + 1}/{total}", callback_data=f"unpurge_noop:{page + 1}:{total}", style="primary"))
        if page < total - 1:
            nav.append(InlineKeyboardButton(text=BTN_NEXT, callback_data=f"unpurge_page:{page + 1}", style="primary"))
    if nav:
        builder.row(*nav)
    return builder.as_markup()
