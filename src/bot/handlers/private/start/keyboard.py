from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.service.vault.buttons import BTN_MY_ITEMS, BTN_SHOP, BTN_SUPPORT, BTN_TOPUP


def kb_start() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text=BTN_SHOP, callback_data="shop_page:0", style="success"),
            InlineKeyboardButton(text=BTN_TOPUP, callback_data="start_get_balance", style="success"),
        ],
        [
            InlineKeyboardButton(text=BTN_MY_ITEMS, callback_data="start_my_items", style="primary"),
        ],
        [
            InlineKeyboardButton(text=BTN_SUPPORT, url="https://t.me/QwertyGeny", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
