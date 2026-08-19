from uuid import uuid4

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message

from src.bot.handlers.public.help.keyboard import kb_help_switch
from src.service.logger import log_app
from src.service.sendmsg import send_msg
from src.service.vault.texts import HELP_INLINE_TITLE, txt_help_body
from src.service.vault.version import get_cached_version


router = Router(name="help")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    log_app.info("/help tg_id={}", message.from_user.id if message.from_user else None)
    await send_msg(message, txt_help_body(), only_caller=True, reply_markup=kb_help_switch())


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
