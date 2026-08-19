from datetime import date, datetime, timezone
from uuid import uuid4

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.bot.handlers.public.setrest.keyboard import kb_setrest_confirm
from src.database.models import User
from src.database.repositories import UserRepository
from src.service.errors import UserNotFound
from src.service.logger import log_app, log_fin
from src.service.vault.roles import Role
from src.service.vault.texts import (
    ERR_NO_RIGHTS,
    SETREST_BAD_DATE,
    SETREST_CANCELLED,
    SETREST_INLINE_TITLE,
    SETREST_NEED_DATE,
    SETREST_PAST,
    SETREST_USAGE,
    SETREST_USER_NOT_FOUND,
    txt_setrest_ok,
    txt_setrest_preview,
)

router = Router(name="inline_setrest")


async def edit_setrest_msg(callback: CallbackQuery, bot: Bot, text: str) -> None:
    if callback.inline_message_id:
        await bot.edit_message_text(text=text, inline_message_id=callback.inline_message_id, parse_mode="HTML", reply_markup=None)
        return

    if callback.message:
        await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=None)


def _article(title: str, text: str, description: str | None = None, markup=None) -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        id=str(uuid4()),
        title=title,
        description=description or title,
        input_message_content=InputTextMessageContent(message_text=text, parse_mode="HTML"),
        reply_markup=markup,
    )


@router.inline_query()
async def inline_setrest(query: InlineQuery, user: User, users: UserRepository):
    raw_q = (query.query or "").strip()
    parts = raw_q.split()

    if not parts:
        return

    cmd = parts[0].lower()

    if cmd not in ("setrest", "sr"):
        return

    if user is None or user.role < Role.OWNER:
        await query.answer([], cache_time=1, is_personal=True)
        return

    if len(parts) == 1:
        log_app.info("inline_setrest usage tg_id={}", query.from_user.id)
        await query.answer([_article(SETREST_INLINE_TITLE, SETREST_USAGE, SETREST_USAGE)], cache_time=1, is_personal=True)
        return

    if len(parts) == 2:
        log_app.info("inline_setrest need date tg_id={}", query.from_user.id)
        await query.answer([_article(SETREST_INLINE_TITLE, SETREST_NEED_DATE, SETREST_NEED_DATE)], cache_time=1, is_personal=True)
        return

    if len(parts) != 3:
        log_app.info("inline_setrest usage tg_id={}", query.from_user.id)
        await query.answer([_article(SETREST_INLINE_TITLE, SETREST_USAGE, SETREST_USAGE)], cache_time=1, is_personal=True)
        return

    token, date_raw = parts[1].lstrip("@"), parts[2]

    try:
        until = datetime.strptime(date_raw, "%d.%m.%Y").date()
    except ValueError:
        log_app.warning("inline_setrest bad date tg_id={} raw={}", query.from_user.id, date_raw)
        await query.answer([_article(SETREST_INLINE_TITLE, SETREST_BAD_DATE, SETREST_BAD_DATE)], cache_time=1, is_personal=True)
        return

    today = datetime.now(timezone.utc).date()

    if until < today:
        log_app.warning("inline_setrest past date tg_id={} raw={}", query.from_user.id, date_raw)
        await query.answer([_article(SETREST_INLINE_TITLE, SETREST_PAST, SETREST_PAST)], cache_time=1, is_personal=True)
        return

    if token.lstrip("-").isdigit():
        tg_id = int(token)
        target, _ = await users.get_or_create(tg_id)
    else:
        target = await users.get_by_username(token)

        if target is None:
            log_app.warning("inline_setrest user not found tg_id={} token={}", query.from_user.id, token)
            await query.answer([_article(SETREST_INLINE_TITLE, SETREST_USER_NOT_FOUND, SETREST_USER_NOT_FOUND)], cache_time=1, is_personal=True)
            return

    until_str = until.strftime("%d.%m.%Y")
    preview = txt_setrest_preview(target.tg_id, target.username, until_str)
    markup = kb_setrest_confirm(target.tg_id, until.isoformat())
    who = f"@{target.username}" if target.username else str(target.tg_id)
    desc = f"{who} · {until_str}"
    log_app.info("inline_setrest preview by={} target={} until={}", query.from_user.id, target.tg_id, until)
    await query.answer([_article(SETREST_INLINE_TITLE, preview, desc, markup)], cache_time=1, is_personal=True)


@router.callback_query(F.data.startswith("setrest_yes:"))
async def clbck_setrest_yes(callback: CallbackQuery, bot: Bot, user: User, users: UserRepository):
    if user is None or user.role < Role.OWNER:
        await callback.answer(ERR_NO_RIGHTS, show_alert=True)
        return

    parts = callback.data.split(":")

    if len(parts) != 3:
        await callback.answer(SETREST_BAD_DATE, show_alert=True)
        return

    try:
        tg_id = int(parts[1])
        until = date.fromisoformat(parts[2])
    except ValueError:
        await callback.answer(SETREST_BAD_DATE, show_alert=True)
        return

    today = datetime.now(timezone.utc).date()

    if until < today:
        await callback.answer(SETREST_PAST, show_alert=True)
        return

    try:
        target = await users.set_rest(tg_id, until)
    except UserNotFound:
        log_app.warning("setrest_yes UserNotFound by={} target={}", user.tg_id, tg_id)
        await callback.answer(SETREST_USER_NOT_FOUND, show_alert=True)
        return

    until_str = until.strftime("%d.%m.%Y")
    text = txt_setrest_ok(target.tg_id, target.username, until_str)
    log_fin.info("setrest ok by={} target={} until={}", user.tg_id, target.tg_id, until)

    try:
        await edit_setrest_msg(callback, bot, text)
    except Exception:
        log_app.warning("setrest_yes edit failed by={} target={}", user.tg_id, tg_id)

    await callback.answer()


@router.callback_query(F.data == "setrest_no")
async def clbck_setrest_no(callback: CallbackQuery, bot: Bot, user: User):
    if user is None or user.role < Role.OWNER:
        await callback.answer(ERR_NO_RIGHTS, show_alert=True)
        return

    log_app.info("setrest_no by={}", user.tg_id)

    try:
        await edit_setrest_msg(callback, bot, SETREST_CANCELLED)
    except Exception:
        log_app.warning("setrest_no edit failed by={}", user.tg_id)

    await callback.answer()
