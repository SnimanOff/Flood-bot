from uuid import uuid4

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.bot.handlers.public.unpurge.helpers import GOOD, unpurge_text
from src.bot.handlers.public.unpurge.keyboard import kb_unpurge
from src.database.models import User
from src.database.repositories import UserRepository
from src.service.logger import log_app
from src.service.vault.roles import Role
from src.service.vault.texts import UNPURGE_EMPTY, UNPURGE_INLINE_TITLE

router = Router(name="inline_unpurge")


@router.inline_query()
async def inline_unpurge(query: InlineQuery, user: User, users: UserRepository):
    q = (query.query or "").strip().lower()

    if q not in ("unpurge", "пощада", "снять", "unp"):
        return

    if user is None or user.role < Role.OWNER:
        await query.answer([], cache_time=1, is_personal=True)
        return

    holders = await users.get_inventory_holders(GOOD)
    log_app.info("inline_unpurge tg_id={} count={}", query.from_user.id, len(holders))
    text = unpurge_text(holders, 0)
    markup = kb_unpurge(holders, 0) if holders else None
    content = InputTextMessageContent(message_text=text, parse_mode="HTML")
    result = InlineQueryResultArticle(id=str(uuid4()), title=UNPURGE_INLINE_TITLE, description=str(len(holders)) if holders else UNPURGE_EMPTY, input_message_content=content, reply_markup=markup)
    await query.answer([result], cache_time=1, is_personal=True)
