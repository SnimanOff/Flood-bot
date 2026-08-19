from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.bot.handlers.public.rmrest.helpers import edit_rmrest_list, plain, rmrest_text
from src.bot.handlers.public.rmrest.keyboard import kb_rmrest
from src.database.models import User
from src.database.repositories import UserRepository
from src.service.errors import UserNotFound
from src.service.logger import log_app, log_fin
from src.service.sendmsg import send_msg
from src.service.vault.roles import Role
from src.service.vault.texts import ERR_NO_RIGHTS, ERR_USER_NOT_FOUND, RMREST_EMPTY, txt_page, txt_rmrest_ok

router = Router(name="rmrest")


@router.message(Command("rmrest"))
async def cmd_rmrest(message: Message, user: User, users: UserRepository):

    if user.role < Role.OWNER:
        await send_msg(message, ERR_NO_RIGHTS, only_caller=True)
        return

    log_app.info("/rmrest tg_id={}", user.tg_id)
    active = await users.get_active_rests()

    if not active:
        await send_msg(message, RMREST_EMPTY, only_caller=True)
        return

    await send_msg(message, rmrest_text(active, 0), reply_markup=kb_rmrest(active, 0), only_caller=True)


@router.callback_query(F.data.startswith("rmrest_page:"))
async def clbck_rmrest_page(callback: CallbackQuery, bot: Bot, user: User, users: UserRepository):

    if user.role < Role.OWNER:
        await callback.answer(ERR_NO_RIGHTS, show_alert=True)
        return

    page = int(callback.data.split(":")[1])
    active = await users.get_active_rests()
    log_app.info("rmrest_page tg_id={} page={}", user.tg_id, page)

    try:

        if active:
            await edit_rmrest_list(callback, bot, rmrest_text(active, page), kb_rmrest(active, page))
        else:
            await edit_rmrest_list(callback, bot, RMREST_EMPTY, None)

    except Exception:
        log_app.warning("rmrest_page edit failed tg_id={} page={}", user.tg_id, page)

    await callback.answer()


@router.callback_query(F.data.startswith("rmrest_noop:"))
async def clbck_rmrest_noop(callback: CallbackQuery, user: User):

    if user.role < Role.OWNER:
        await callback.answer(ERR_NO_RIGHTS, show_alert=True)
        return

    parts = callback.data.split(":")
    await callback.answer(txt_page(parts[1], parts[2]))


@router.callback_query(F.data.startswith("rmrest_take:"))
async def clbck_rmrest_take(callback: CallbackQuery, bot: Bot, user: User, users: UserRepository):

    if user.role < Role.OWNER:
        await callback.answer(ERR_NO_RIGHTS, show_alert=True)
        return

    target_id = int(callback.data.split(":")[1])
    log_app.info("rmrest_take tg_id={} target={}", user.tg_id, target_id)

    try:
        updated = await users.clear_rest(target_id)
    except UserNotFound:
        await callback.answer(ERR_USER_NOT_FOUND, show_alert=True)
        return

    log_fin.info("rmrest ok by={} target={}", user.tg_id, target_id)
    await callback.answer(plain(txt_rmrest_ok(target_id, updated.username)), show_alert=True)
    active = await users.get_active_rests()

    try:

        if active:
            await edit_rmrest_list(callback, bot, rmrest_text(active, 0), kb_rmrest(active, 0))
        else:
            await edit_rmrest_list(callback, bot, RMREST_EMPTY, None)

    except Exception:
        log_app.warning("rmrest_take edit failed tg_id={} target={}", user.tg_id, target_id)
