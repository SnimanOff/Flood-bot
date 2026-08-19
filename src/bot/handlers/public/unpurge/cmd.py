from uuid import uuid4
import math
import re

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message

from src.bot.handlers.public.unpurge.keyboard import PER_PAGE, kb_unpurge, kb_unpurge_switch
from src.database.models import User
from src.database.repositories import UserRepository
from src.service.errors import NotEnoughInventory, UserNotFound
from src.service.logger import log_app, log_fin
from src.service.sendmsg import send_msg
from src.service.vault.goods import Goods
from src.service.vault.roles import Role
from src.service.vault.texts import ERR_NO_RIGHTS, INLINE_HINT, UNPURGE_EMPTY, UNPURGE_FAIL, UNPURGE_INLINE_TITLE, UNPURGE_NONE, txt_page, txt_unpurge_header, txt_unpurge_ok


router = Router(name="unpurge")
GOOD = str(Goods.PURGE_IMMUNITY)


def unpurge_text(holders: list, page: int) -> str:
    total = max(1, math.ceil(len(holders) / PER_PAGE)) if holders else 1
    page = max(0, min(page, total - 1))
    if not holders:
        return UNPURGE_EMPTY
    return txt_unpurge_header(page, total, len(holders))


def _plain(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


async def edit_unpurge_list(callback: CallbackQuery, bot: Bot, text: str, reply_markup=None) -> None:
    if callback.inline_message_id:
        await bot.edit_message_text(text=text, inline_message_id=callback.inline_message_id, parse_mode="HTML", reply_markup=reply_markup)
        return
    if callback.message:
        await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=reply_markup)


@router.message(Command("unpurge"))
async def cmd_unpurge(message: Message, user: User, users: UserRepository):

    if user.role < Role.OWNER:
        await send_msg(message, ERR_NO_RIGHTS, only_caller=True)
        return
    
    log_app.info("/unpurge tg_id={}", user.tg_id)
    holders = await users.get_inventory_holders(GOOD)

    if message.chat.type == "private":
        if not holders:
            await send_msg(message, UNPURGE_EMPTY, reply_markup=kb_unpurge_switch())
        else:
            await send_msg(message, unpurge_text(holders, 0), reply_markup=kb_unpurge(holders, 0))

    else:
        await send_msg(message, INLINE_HINT, reply_markup=kb_unpurge_switch(), only_caller=True)


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


@router.callback_query(F.data.startswith("unpurge_page:"))
async def clbck_unpurge_page(callback: CallbackQuery, bot: Bot, user: User, users: UserRepository):

    if user.role < Role.OWNER:
        await callback.answer(ERR_NO_RIGHTS, show_alert=True)
        return
    
    page = int(callback.data.split(":")[1])
    holders = await users.get_inventory_holders(GOOD)
    log_app.info("unpurge_page tg_id={} page={}", user.tg_id, page)

    try:
        if holders:
            await edit_unpurge_list(callback, bot, unpurge_text(holders, page), kb_unpurge(holders, page))
        else:
            await edit_unpurge_list(callback, bot, UNPURGE_EMPTY, None)

    except Exception:
        log_app.warning("unpurge_page edit failed tg_id={} page={}", user.tg_id, page)

    await callback.answer()


@router.callback_query(F.data.startswith("unpurge_noop:"))
async def clbck_unpurge_noop(callback: CallbackQuery, user: User):

    if user.role < Role.OWNER:
        await callback.answer(ERR_NO_RIGHTS, show_alert=True)
        return
    
    parts = callback.data.split(":")
    await callback.answer(txt_page(parts[1], parts[2]))


@router.callback_query(F.data.startswith("unpurge_take:"))
async def clbck_unpurge_take(callback: CallbackQuery, bot: Bot, user: User, users: UserRepository):

    if user.role < Role.OWNER:
        await callback.answer(ERR_NO_RIGHTS, show_alert=True)
        return
    
    target_id = int(callback.data.split(":")[1])
    log_app.info("unpurge_take tg_id={} target={}", user.tg_id, target_id)

    try:
        updated = await users.take_inventory(target_id, GOOD, 1)
    except UserNotFound:
        await callback.answer(UNPURGE_FAIL, show_alert=True)
        return
    except NotEnoughInventory:
        await callback.answer(UNPURGE_NONE, show_alert=True)
        holders = await users.get_inventory_holders(GOOD)
        try:
            if holders:
                await edit_unpurge_list(callback, bot, unpurge_text(holders, 0), kb_unpurge(holders, 0))
            else:
                await edit_unpurge_list(callback, bot, UNPURGE_EMPTY, None)
        except Exception:
            log_app.warning("unpurge_take edit failed tg_id={} target={}", user.tg_id, target_id)
        return
    
    left = int((updated.inventory or {}).get(GOOD, 0) or 0)
    log_fin.info("unpurge ok by={} target={} left={}", user.tg_id, target_id, left)
    await callback.answer(_plain(txt_unpurge_ok(target_id, updated.username, left)), show_alert=True)
    holders = await users.get_inventory_holders(GOOD)
    
    try:
        if holders:
            await edit_unpurge_list(callback, bot, unpurge_text(holders, 0), kb_unpurge(holders, 0))
        else:
            await edit_unpurge_list(callback, bot, UNPURGE_EMPTY, None)
    except Exception:
        log_app.warning("unpurge_take edit failed tg_id={} target={}", user.tg_id, target_id)
