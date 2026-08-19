import math

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.service.vault.buttons import BTN_BACK, BTN_NEXT
from src.service.vault.texts import txt_rmrest_btn


PER_PAGE = 4


def kb_rmrest(users: list, page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    total = max(1, math.ceil(len(users) / PER_PAGE)) if users else 1
    page = max(0, min(page, total - 1))
    chunk = users[page * PER_PAGE : (page + 1) * PER_PAGE]

    for u in chunk:
        until_str = u.rest_until.strftime("%d.%m.%Y") if u.rest_until else "—"
        label = txt_rmrest_btn(u.username, u.tg_id, until_str)
        builder.button(text=label, callback_data=f"rmrest_take:{u.tg_id}", style="primary")
    builder.adjust(1)

    nav = []

    if total > 1:

        if page > 0:
            nav.append(InlineKeyboardButton(text=BTN_BACK, callback_data=f"rmrest_page:{page - 1}", style="primary"))

        nav.append(InlineKeyboardButton(text=f"{page + 1}/{total}", callback_data=f"rmrest_noop:{page + 1}:{total}", style="primary"))

        if page < total - 1:
            nav.append(InlineKeyboardButton(text=BTN_NEXT, callback_data=f"rmrest_page:{page + 1}", style="primary"))

    if nav:
        builder.row(*nav)

    return builder.as_markup()
