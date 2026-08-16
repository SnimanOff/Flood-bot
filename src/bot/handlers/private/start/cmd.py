from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.bot.handlers.private.start.keyboard import kb_start, kb_shop
from src.service.vault.goods import get_goods 
from src.database.repositories import UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.media import START_MEDIA

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message, users: UserRepository) -> None:
    await users.get_or_create(message.from_user.id, message.from_user.username)

    await send_msg(message=message, text=f"Привет, {message.from_user.first_name}!", media=START_MEDIA, reply_markup=kb_start())

@router.callback_query(F.data.startswith("shop_noop:"))
async def shop_noop(call: CallbackQuery):

    _, cur, total = call.data.split(":")

    await call.answer(f"Страница {cur} из {total}")

@router.callback_query(F.data.startswith("shop_page:"))
async def shop_page(call: CallbackQuery):
    page = int(call.data.split(":")[1])
    
    await call.message.edit_reply_markup(reply_markup=kb_shop(get_goods(), page))
    await call.answer()

@router.callback_query(F.data == "shop_select:purge_immunity")