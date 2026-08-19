import math
import re

from aiogram import Bot
from aiogram.types import CallbackQuery

from src.bot.handlers.public.unpurge.keyboard import PER_PAGE
from src.service.vault.goods import Goods
from src.service.vault.texts import UNPURGE_EMPTY, txt_unpurge_header

GOOD = str(Goods.PURGE_IMMUNITY)


def unpurge_text(holders: list, page: int) -> str:
    total = max(1, math.ceil(len(holders) / PER_PAGE)) if holders else 1
    page = max(0, min(page, total - 1))

    if not holders:
        return UNPURGE_EMPTY

    return txt_unpurge_header(page, total, len(holders))


def plain(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


async def edit_unpurge_list(callback: CallbackQuery, bot: Bot, text: str, reply_markup=None) -> None:
    if callback.inline_message_id:
        await bot.edit_message_text(text=text, inline_message_id=callback.inline_message_id, parse_mode="HTML", reply_markup=reply_markup)
        return

    if callback.message:
        await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
