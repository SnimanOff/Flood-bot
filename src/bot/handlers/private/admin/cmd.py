from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.database.models import User
from src.database.repositories import UserRepository
from src.service.errors import UserNotFound
from src.service.logger import log_app
from src.service.sendmsg import send_msg
from src.service.vault.roles import Role
from src.service.vault.texts import (
    ERR_NO_RIGHTS,
    ERR_USER_NOT_FOUND,
    SETROLE_BAD_ROLE,
    SETROLE_LAST_ROOT,
    SETROLE_NEED_TARGET,
    SETROLE_USAGE,
    SETROLE_USER_NOT_FOUND,
    txt_setrole_ok,
)

router = Router(name="admin_roles")

ROLE_MAP = {
    "user": Role.USER,
    "moderator": Role.MODERATOR,
    "mod": Role.MODERATOR,
    "admin": Role.ADMIN,
    "owner": Role.OWNER,
    "root": Role.ROOT,
}

ROLE_NAME = {
    Role.USER: "user",
    Role.MODERATOR: "moderator",
    Role.ADMIN: "admin",
    Role.OWNER: "owner",
    Role.ROOT: "root",
}


def parse_role(raw: str) -> Role | None:
    return ROLE_MAP.get(raw.strip().lower())


async def resolve_target(message: Message, users: UserRepository, token: str | None) -> tuple[int | None, str | None]:
    reply_user = message.reply_to_message.from_user if message.reply_to_message else None

    if reply_user is not None and not reply_user.is_bot:
        await users.get_or_create(reply_user.id, reply_user.username)
        return reply_user.id, None

    if not token:
        return None, SETROLE_NEED_TARGET

    if token.lstrip("-").isdigit():
        tg_id = int(token)
        await users.get_or_create(tg_id)
        return tg_id, None

    user = await users.get_by_username(token)

    if user is None:
        return None, SETROLE_USER_NOT_FOUND

    return user.tg_id, None


@router.message(Command("setrole"), F.chat.type == "private")
async def cmd_setrole(message: Message, command: CommandObject, user: User, users: UserRepository) -> None:
    log_app.info("/setrole tg_id={} args={}", message.from_user.id if message.from_user else None, command.args)

    if user.role < Role.ROOT:
        log_app.warning("setrole denied tg_id={} role={}", user.tg_id, user.role)
        await send_msg(message, ERR_NO_RIGHTS, only_caller=True)
        return

    args = (command.args or "").split()
    reply_user = message.reply_to_message.from_user if message.reply_to_message else None
    has_reply = reply_user is not None and not reply_user.is_bot

    if has_reply and len(args) == 1:
        role_raw = args[0]
        target_token = None
    elif len(args) == 2:
        target_token, role_raw = args[0], args[1]
    else:
        await send_msg(message, SETROLE_USAGE, only_caller=True)
        return

    new_role = parse_role(role_raw)

    if new_role is None:
        await send_msg(message, SETROLE_BAD_ROLE, only_caller=True)
        return

    target_id, error = await resolve_target(message, users, None if has_reply else target_token)

    if error:
        await send_msg(message, error, only_caller=True)
        return

    if target_id == user.tg_id and new_role < Role.ROOT:
        if not await users.has_other_root(user.tg_id):
            await send_msg(message, SETROLE_LAST_ROOT, only_caller=True)
            return

    try:
        target = await users.set_role(target_id, new_role)
    except UserNotFound:
        log_app.warning("setrole UserNotFound target_id={}", target_id)
        await send_msg(message, ERR_USER_NOT_FOUND, only_caller=True)
        return

    role_name = ROLE_NAME.get(target.role, str(target.role))
    log_app.info("setrole by tg_id={} target={} role={}", user.tg_id, target.tg_id, role_name)
    await send_msg(message, txt_setrole_ok(target.tg_id, role_name), only_caller=True)
