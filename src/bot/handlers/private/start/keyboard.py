from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import math


def kb_start() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="Магазин", callback_data="shop_page:0"),
            InlineKeyboardButton(text="Пополнить", callback_data="start_get_balance"),
        ],
        [
            InlineKeyboardButton(text="Мои награды", callback_data="start_my_items"),
        ],
        [
            InlineKeyboardButton(text="Поддержка", url="https://t.me/QwertyGeny"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def kb_shop(goods: list, page: int = 0) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    total = max(1, math.ceil(len(goods) / 4))
    page = max(0, min(page, total - 1))
    chunk = goods[page * 4 : (page + 1) * 4]

    for good in chunk:
        builder.button(text=str(good), callback_data=f"shop_select:{good}")

    builder.adjust(2)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="<", callback_data=f"shop_page:{page - 1}"))

    nav.append(InlineKeyboardButton(text=f"{page + 1}/{total}", callback_data=f"shop_noop:{page + 1}:{total}"))

    if page < total - 1:
        nav.append(InlineKeyboardButton(text=">", callback_data=f"shop_page:{page + 1}"))

    builder.row(*nav)
    builder.row(InlineKeyboardButton(text="Назад", callback_data="start_menu"))

    return builder.as_markup()

