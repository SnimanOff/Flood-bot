from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.service.vault.buttons import BTN_BACK_MENU

def kb_my_items() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=BTN_BACK_MENU, callback_data="start_menu"),
    ]])
