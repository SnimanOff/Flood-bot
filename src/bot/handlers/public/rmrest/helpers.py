import math
import re

from aiogram import Bot
from aiogram.types import CallbackQuery

from src.bot.handlers.public.rmrest.keyboard import PER_PAGE
from src.service.vault.texts import RMREST_EMPTY, txt_rmrest_header


def rmrest_text(users: list, page: int) -> str:
    total = max(1, math.ceil(len(users) / PER_PAGE)) if users else 1
    page = max(0, min(page, total - 1))

    if not users:
        return RMREST_EMPTY

    return txt_rmrest_header(page, total, len(users))


def plain(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


async def edit_rmrest_list(callback: CallbackQuery, bot: Bot, text: str, reply_markup=None) -> None:

    if callback.inline_message_id:
        await bot.edit_message_text(text=text, inline_message_id=callback.inline_message_id, parse_mode="HTML", reply_markup=reply_markup)
        return

    if callback.message:
        await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
