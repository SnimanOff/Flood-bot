from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.service.vault.buttons import BTN_HELP


def kb_help_switch() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=BTN_HELP, switch_inline_query_current_chat="help")]])
