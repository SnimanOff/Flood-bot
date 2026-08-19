from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.database.models import User
from src.database.repositories import UserRepository
from src.service.errors import UserNotFound
from src.service.logger import log_app, log_fin
from src.service.sendmsg import send_msg
from src.service.vault.roles import Role
from src.service.vault.texts import (
    ERR_NO_RIGHTS,
    SETREST_BAD_DATE,
    SETREST_CMD_USAGE,
    SETREST_NEED_USER,
    SETREST_PAST,
    SETREST_USER_NOT_FOUND,
    txt_setrest_ok,
)

router = Router(name="setrest")


def parse_date(raw: str):
    try:
        return datetime.strptime(raw, "%d.%m.%Y").date()
    except ValueError:
        return None


async def resolve_target(message: Message, users: UserRepository, token: str | None) -> tuple[int | None, str | None]:
    reply_user = message.reply_to_message.from_user if message.reply_to_message else None

    if reply_user is not None and not reply_user.is_bot:
        await users.get_or_create(reply_user.id, reply_user.username)
        return reply_user.id, None

    if not token:
        return None, SETREST_NEED_USER

    token = token.lstrip("@")

    if token.lstrip("-").isdigit():
        tg_id = int(token)
        await users.get_or_create(tg_id)
        return tg_id, None

    found = await users.get_by_username(token)

    if found is None:
        return None, SETREST_USER_NOT_FOUND

    return found.tg_id, None


@router.message(Command("setrest"))
async def cmd_setrest(message: Message, command: CommandObject, user: User, users: UserRepository) -> None:
    log_app.info("/setrest tg_id={} args={}", message.from_user.id if message.from_user else None, command.args)

    if user is None or user.role < Role.OWNER:
        log_app.warning("setrest denied tg_id={} role={}", getattr(user, "tg_id", None), getattr(user, "role", None))
        await send_msg(message, ERR_NO_RIGHTS, only_caller=True)
        return

    args = (command.args or "").split()
    reply_user = message.reply_to_message.from_user if message.reply_to_message else None
    has_reply = reply_user is not None and not reply_user.is_bot

    if has_reply and len(args) == 1:
        date_raw = args[0]
        target_token = None
    elif len(args) == 2:
        target_token, date_raw = args[0], args[1]
    else:
        await send_msg(message, SETREST_CMD_USAGE, only_caller=True)
        return

    until = parse_date(date_raw)

    if until is None:
        await send_msg(message, SETREST_BAD_DATE, only_caller=True)
        return

    today = datetime.now(timezone.utc).date()

    if until < today:
        await send_msg(message, SETREST_PAST, only_caller=True)
        return

    target_id, error = await resolve_target(message, users, None if has_reply else target_token)

    if error:
        await send_msg(message, error, only_caller=True)
        return

    try:
        target = await users.set_rest(target_id, until)
    except UserNotFound:
        log_app.warning("setrest UserNotFound target_id={}", target_id)
        await send_msg(message, SETREST_USER_NOT_FOUND, only_caller=True)
        return

    until_str = until.strftime("%d.%m.%Y")
    log_fin.info("setrest cmd by={} target={} until={}", user.tg_id, target.tg_id, until)
    await send_msg(message, txt_setrest_ok(target.tg_id, target.username, until_str), only_caller=True)
