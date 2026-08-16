from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
