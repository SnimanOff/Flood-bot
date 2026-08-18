from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.bot.handlers.private.start.keyboard import kb_start
from src.database.models import User
from src.service.sendmsg import send_msg
from src.service.vault.media import START_MEDIA
from src.service.vault.texts import txt_start_hello

router = Router(name="start")


@router.message(Command("start"), F.chat.type == "private")
async def cmd_start(message: Message, user: User) -> None:
    await send_msg(message=message, text=txt_start_hello(message.from_user.first_name), media=START_MEDIA, reply_markup=kb_start())

@router.callback_query(F.data == "start_menu", F.message.chat.type == "private")
async def clbck_start_menu(callback: CallbackQuery, user: User) -> None:
    text = txt_start_hello(callback.from_user.first_name)

    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=kb_start())
    else:
        await callback.message.edit_text(text=text, reply_markup=kb_start())

    await callback.answer()
