from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.handlers.public.help.keyboard import kb_help_switch
from src.service.logger import log_app
from src.service.sendmsg import send_msg
from src.service.vault.texts import txt_help_body

router = Router(name="help")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    log_app.info("/help tg_id={}", message.from_user.id if message.from_user else None)
    await send_msg(message, txt_help_body(), only_caller=True, reply_markup=kb_help_switch())
