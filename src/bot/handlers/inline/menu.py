from uuid import uuid4

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.bot.handlers.public.rests.format import format_rests
from src.bot.handlers.public.unpurge.helpers import GOOD, unpurge_text
from src.bot.handlers.public.unpurge.keyboard import kb_unpurge
from src.database.models import User
from src.database.repositories import UserRepository
from src.service.logger import log_app
from src.service.vault.roles import Role
from src.service.vault.texts import (
    HELP_INLINE_TITLE,
    RESTS_EMPTY,
    RESTS_INLINE_TITLE,
    UNPURGE_EMPTY,
    UNPURGE_INLINE_TITLE,
    txt_help_body,
)
from src.service.vault.version import get_cached_version

router = Router(name="inline_menu")


@router.inline_query()
async def inline_menu(query: InlineQuery, user: User, users: UserRepository):
    q = (query.query or "").strip().lower()

    if q != "":
        return

    log_app.info("inline_menu tg_id={}", query.from_user.id)
    results: list[InlineQueryResultArticle] = []

    results.append(InlineQueryResultArticle(
        id=str(uuid4()),
        title=HELP_INLINE_TITLE,
        description=f"v{get_cached_version()}",
        input_message_content=InputTextMessageContent(message_text=txt_help_body(), parse_mode="HTML"),
    ))

    active = await users.get_active_rests()
    rests_text = format_rests(active)
    results.append(InlineQueryResultArticle(
        id=str(uuid4()),
        title=RESTS_INLINE_TITLE,
        description=str(len(active)) if active else RESTS_EMPTY,
        input_message_content=InputTextMessageContent(message_text=rests_text, parse_mode="HTML"),
    ))

    if user is not None and user.role >= Role.OWNER:
        holders = await users.get_inventory_holders(GOOD)
        text = unpurge_text(holders, 0)
        markup = kb_unpurge(holders, 0) if holders else None
        results.append(InlineQueryResultArticle(
            id=str(uuid4()),
            title=UNPURGE_INLINE_TITLE,
            description=str(len(holders)) if holders else UNPURGE_EMPTY,
            input_message_content=InputTextMessageContent(message_text=text, parse_mode="HTML"),
            reply_markup=markup,
        ))

    await query.answer(results, cache_time=1, is_personal=True)
