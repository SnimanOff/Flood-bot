from uuid import uuid4

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.bot.handlers.public.rests.format import format_rests
from src.database.repositories import UserRepository
from src.service.logger import log_app
from src.service.vault.texts import RESTS_EMPTY, RESTS_INLINE_TITLE

router = Router(name="inline_rests")


@router.inline_query()
async def inline_rests(query: InlineQuery, users: UserRepository) -> None:
    q = (query.query or "").strip().lower()

    if q not in ("rests", "рест", "ресты"):
        return

    active = await users.get_active_rests()
    log_app.info("inline_rests tg_id={} count={}", query.from_user.id, len(active))
    text = format_rests(active)
    content = InputTextMessageContent(message_text=text, parse_mode="HTML")
    result = InlineQueryResultArticle(id=str(uuid4()), title=RESTS_INLINE_TITLE, description=str(len(active)) if active else RESTS_EMPTY, input_message_content=content)
    await query.answer([result], cache_time=5, is_personal=True)
