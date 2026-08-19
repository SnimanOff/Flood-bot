from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.handlers.public.rests.format import format_rests
from src.bot.handlers.public.rests.keyboard import kb_rests_inline
from src.database.repositories import UserRepository
from src.service.logger import log_app
from src.service.sendmsg import send_msg
from src.service.vault.texts import INLINE_HINT

router = Router(name="rests")


@router.message(Command("rests"))
async def cmd_rests(message: Message, users: UserRepository) -> None:
    active = await users.get_active_rests()
    log_app.info("/rests tg_id={} count={}", message.from_user.id if message.from_user else None, len(active))
    text = format_rests(active)

    if message.chat.type == "private":
        await send_msg(message, text, reply_markup=kb_rests_inline())
    else:
        await send_msg(message, INLINE_HINT, reply_markup=kb_rests_inline(), only_caller=True)
