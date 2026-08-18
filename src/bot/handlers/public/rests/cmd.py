from uuid import uuid4

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message

from src.bot.handlers.public.rests.keyboard import kb_rests_inline
from src.database.models import User
from src.database.repositories import UserRepository
from src.service.logger import log_app
from src.service.sendmsg import send_msg
from src.service.vault.texts import RESTS_EMPTY, RESTS_INLINE_HINT, RESTS_INLINE_TITLE, txt_rests_line, txt_rests_list


router = Router(name="rests")


def format_rests(users: list[User]) -> str:
    lines = []
    for u in users:
        until_str = u.rest_until.strftime("%d.%m.%Y") if u.rest_until else "—"
        lines.append(txt_rests_line(u.tg_id, u.username, until_str))
    return txt_rests_list(lines)


@router.message(Command("rests"))
async def cmd_rests(message: Message, users: UserRepository) -> None:
    active = await users.get_active_rests()
    log_app.info("/rests tg_id={} count={}", message.from_user.id if message.from_user else None, len(active))
    text = format_rests(active)
    if message.chat.type == "private":
        await send_msg(message, text, reply_markup=kb_rests_inline())
    else:
        await send_msg(message, RESTS_INLINE_HINT, reply_markup=kb_rests_inline(), only_caller=True)


@router.inline_query()
async def inline_rests(query: InlineQuery, users: UserRepository) -> None:
    q = (query.query or "").strip().lower()
    if q not in ("", "rests", "рест", "ресты"):
        return
    active = await users.get_active_rests()
    log_app.info("inline_rests tg_id={} count={}", query.from_user.id, len(active))
    text = format_rests(active)
    content = InputTextMessageContent(message_text=text, parse_mode="HTML")
    result = InlineQueryResultArticle(id=str(uuid4()), title=RESTS_INLINE_TITLE, description=str(len(active)) if active else RESTS_EMPTY, input_message_content=content)
    await query.answer([result], cache_time=5, is_personal=True)
