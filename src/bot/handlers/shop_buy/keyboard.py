from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.service.vault.buttons import BTN_CANCEL, BTN_CONFIRM


def kb_rest_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_CONFIRM, callback_data="rest_confirm:yes", style="success")],
        [InlineKeyboardButton(text=BTN_CANCEL, callback_data="rest_confirm:no", style="danger")],
    ])
