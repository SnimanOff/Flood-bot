from uuid import uuid4

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message

from src.database.models import User
from src.database.repositories import UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.buttons import BTN_RESTS_LIST
from src.service.vault.texts import RESTS_EMPTY, RESTS_INLINE_HINT, RESTS_INLINE_TITLE, txt_rests_line, txt_rests_list


router = Router(name="rests")


def format_rests(users: list[User]) -> str:
    lines = []
    for u in users:
        until_str = u.rest_until.strftime("%d.%m.%Y") if u.rest_until else "—"
        lines.append(txt_rests_line(u.tg_id, u.username, until_str))
    return txt_rests_list(lines)


def kb_rests_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=BTN_RESTS_LIST, switch_inline_query_current_chat="rests")]])


@router.message(Command("rests"))
async def cmd_rests(message: Message, users: UserRepository) -> None:
    active = await users.get_active_rests()
    text = format_rests(active)
    if message.chat.type == "private":
        await send_msg(message, text, reply_markup=kb_rests_inline())
    else:
        await send_msg(message, RESTS_INLINE_HINT, reply_markup=kb_rests_inline(), only_caller=True)


@router.inline_query()
async def inline_rests(query: InlineQuery, users: UserRepository) -> None:
    q = (query.query or "").strip().lower()
    if q not in ("", "rests", "рест", "ресты"):
        await query.answer([], cache_time=5, is_personal=True)
        return

    active = await users.get_active_rests()
    text = format_rests(active)
    result = InlineQueryResultArticle(
        id=str(uuid4()),
        title=RESTS_INLINE_TITLE,
        description=str(len(active)) if active else RESTS_EMPTY,
        input_message_content=InputTextMessageContent(message_text=text, parse_mode="HTML"),
    )
    await query.answer([result], cache_time=5, is_personal=True)
