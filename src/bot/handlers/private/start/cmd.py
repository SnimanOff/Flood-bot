from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.bot.handlers.private.start.keyboard import kb_start
from src.database.repositories import UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.media import START_MEDIA

router = Router(name="start")


@router.message(Command("start"), F.chat.type == "private")
async def cmd_start(message: Message, users: UserRepository) -> None:
    await users.get_or_create(message.from_user.id, message.from_user.username)

    await send_msg(message=message, text=f"Привет, {message.from_user.first_name}!", media=START_MEDIA, reply_markup=kb_start())

# ---------------- меню ----------------

@router.callback_query(F.data == "start_menu", F.message.chat.type == "private")
async def clbck_start_menu(callback: CallbackQuery, users: UserRepository) -> None:
    await users.get_or_create(callback.from_user.id, callback.from_user.username)

    text = f"Привет, {callback.from_user.first_name}"

    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=kb_start())
    else:
        await callback.message.edit_text(text=text, reply_markup=kb_start())

    await callback.answer()
