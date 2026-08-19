from uuid import uuid4

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.bot.handlers.public.rmrest.helpers import rmrest_text
from src.bot.handlers.public.rmrest.keyboard import kb_rmrest
from src.database.models import User
from src.database.repositories import UserRepository
from src.service.logger import log_app
from src.service.vault.roles import Role
from src.service.vault.texts import RMREST_EMPTY, RMREST_INLINE_TITLE

router = Router(name="inline_rmrest")


@router.inline_query()
async def inline_rmrest(query: InlineQuery, user: User, users: UserRepository):
    q = (query.query or "").strip().lower()

    if q not in ("rmrest", "снятьрест", "rr"):
        return

    if user is None or user.role < Role.OWNER:
        await query.answer([], cache_time=1, is_personal=True)
        return

    active = await users.get_active_rests()
    log_app.info("inline_rmrest tg_id={} count={}", query.from_user.id, len(active))
    text = rmrest_text(active, 0)
    markup = kb_rmrest(active, 0) if active else None
    content = InputTextMessageContent(message_text=text, parse_mode="HTML")
    result = InlineQueryResultArticle(id=str(uuid4()), title=RMREST_INLINE_TITLE, description=str(len(active)) if active else RMREST_EMPTY, input_message_content=content, reply_markup=markup)
    await query.answer([result], cache_time=1, is_personal=True)
