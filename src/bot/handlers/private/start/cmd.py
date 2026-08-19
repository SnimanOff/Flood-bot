from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.bot.handlers.private.start.keyboard import kb_start
from src.database.models import User
from src.service.logger import log_app
from src.service.sendmsg import send_msg
from src.service.vault.media import START_MEDIA
from src.service.vault.texts import txt_start_hello
from src.service.vault.version import get_version_info

router = Router(name="start")


@router.message(Command("start"), F.chat.type == "private")
async def cmd_start(message: Message, user: User) -> None:
    log_app.info("/start tg_id={}", message.from_user.id)
    version, updated = await get_version_info()
    name = message.from_user.first_name or "друг"
    text = txt_start_hello(name, version, updated)
    await send_msg(message=message, text=text, media=START_MEDIA, reply_markup=kb_start())


@router.callback_query(F.data == "start_menu", F.message.chat.type == "private")
async def clbck_start_menu(callback: CallbackQuery, user: User) -> None:
    log_app.info("start_menu tg_id={}", callback.from_user.id)
    version, updated = await get_version_info()
    name = callback.from_user.first_name or "друг"
    text = txt_start_hello(name, version, updated)
    await send_msg(callback.message, text, media=START_MEDIA, reply_markup=kb_start(), edit=True)
    await callback.answer()
