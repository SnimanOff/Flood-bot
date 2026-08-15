from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from html import escape

from src.bot.handlers.private.start.keyboard import kb_start
from src.database.repositories import UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.media import START_MEDIA

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message, users: UserRepository) -> None:
    await users.get_or_create(message.from_user.id, message.from_user.username)

    await send_msg(message=message, text=f"Привет, {message.from_user.first_name}!", media=START_MEDIA, reply_markup=kb_start())
