from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import math

from src.service.vault.buttons import BTN_BACK, BTN_BACK_MENU, BTN_BUY


def kb_shop(goods: list, page: int = 0) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    total = max(1, math.ceil(len(goods) / 4))
    page = max(0, min(page, total - 1))
    chunk = goods[page * 4 : (page + 1) * 4]

    for good in chunk:
        builder.button(text=good["title"], callback_data=f"shop_select:{good['id']}", style="primary")

    builder.adjust(2)

    nav = []
    if total > 1:
        if page > 0:
            nav.append(InlineKeyboardButton(text=BTN_BACK, callback_data=f"shop_page:{page - 1}", style="primary"))
        nav.append(InlineKeyboardButton(text=f"{page + 1}/{total}", callback_data=f"shop_noop:{page + 1}:{total}", style="primary"))
        if page < total - 1:
            nav.append(InlineKeyboardButton(text=">", callback_data=f"shop_page:{page + 1}", style="primary"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text=BTN_BACK_MENU, callback_data="start_menu", style="primary"))

    return builder.as_markup()


def kb_buy(good_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=BTN_BUY, callback_data=f"shop_buy:{good_id}", style="success")],
        [InlineKeyboardButton(text=BTN_BACK, callback_data="shop_page:0", style="primary")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
