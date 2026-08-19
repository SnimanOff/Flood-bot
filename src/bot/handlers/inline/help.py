from uuid import uuid4

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.service.logger import log_app
from src.service.vault.texts import HELP_INLINE_TITLE, txt_help_body
from src.service.vault.version import get_cached_version

router = Router(name="inline_help")


@router.inline_query()
async def inline_help(query: InlineQuery) -> None:
    q = (query.query or "").strip().lower()

    if q not in ("help", "справка", "помощь", "?"):
        return

    log_app.info("inline_help tg_id={}", query.from_user.id)
    result = InlineQueryResultArticle(
        id=str(uuid4()),
        title=HELP_INLINE_TITLE,
        description=f"v{get_cached_version()}",
        input_message_content=InputTextMessageContent(message_text=txt_help_body(), parse_mode="HTML"),
    )
    await query.answer([result], cache_time=10, is_personal=True)
