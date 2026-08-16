from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_admin_request(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Принять", callback_data=f"bal_ok:{request_id}", style="success"),
        InlineKeyboardButton(text="Отказать", callback_data=f"bal_no:{request_id}", style="danger"),
    ]])
