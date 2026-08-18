from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.service.vault.buttons import BTN_RESTS_LIST


def kb_rests_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=BTN_RESTS_LIST, switch_inline_query_current_chat="rests")]])
