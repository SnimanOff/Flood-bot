from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.service.vault.buttons import BTN_CANCEL, BTN_CONFIRM


def kb_setrest_confirm(tg_id: int, until_iso: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_CONFIRM, callback_data=f"setrest_yes:{tg_id}:{until_iso}", style="success")],
        [InlineKeyboardButton(text=BTN_CANCEL, callback_data="setrest_no", style="danger")],
    ])