from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.service.vault.buttons import BTN_ACCEPT, BTN_REJECT


def kb_admin_request(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=BTN_ACCEPT, callback_data=f"bal_ok:{request_id}", style="success"),
        InlineKeyboardButton(text=BTN_REJECT, callback_data=f"bal_no:{request_id}", style="danger"),
    ]])
