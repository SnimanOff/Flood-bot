from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.database.models import User
from src.database.repositories import UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.media import GM_DENIED_MEDIA, GM_MEDIA, GM_OK_MEDIA, GM_USAGE_MEDIA
from src.service.vault.roles import Role

router = Router(name="gm")


def parse_amount(raw: str) -> int | None:

    try:
        amount = int(raw)

    except ValueError:
        return None
    
    if amount == 0:
        return None
    
    return amount


async def resolve_target(message: Message, users: UserRepository, token: str | None) -> tuple[int | None, str | None]:

    reply_user = message.reply_to_message.from_user if message.reply_to_message else None

    if reply_user is not None and not reply_user.is_bot:
        await users.get_or_create(reply_user.id, reply_user.username)
        return reply_user.id, None

    if not token:
        return None, "Укажи пользователя: reply или /gm <id|@user> <сумма>"

    if token.lstrip("-").isdigit():
        tg_id = int(token)
        await users.get_or_create(tg_id)
        return tg_id, None

    user = await users.get_by_username(token)
    if user is None:
        return None, "Пользователь не найден в БД (нужен id или чтобы он писал боту)"
    
    return user.tg_id, None


@router.message(Command("gm"))
async def cmd_gm(message: Message, command: CommandObject, user: User, users: UserRepository) -> None:
    caller = user

    if caller.role < Role.OWNER:
        await send_msg(message, "Недостаточно прав", media=GM_DENIED_MEDIA, only_caller=True)
        return

    args = (command.args or "").split()
    reply_user = message.reply_to_message.from_user if message.reply_to_message else None
    has_reply = reply_user is not None and not reply_user.is_bot

    if has_reply and len(args) == 1:
        amount = parse_amount(args[0])
        target_token = None
    elif len(args) == 2:
        target_token, amount_raw = args[0], args[1]
        amount = parse_amount(amount_raw)
    else:
        await send_msg(message, "Использование:\n/gm <id|@user> <сумма>\nили reply: /gm <сумма>", media=GM_USAGE_MEDIA, only_caller=True)
        return

    if amount is None:
        await send_msg(message, "Сумма должна быть целым числом ≠ 0", media=GM_USAGE_MEDIA, only_caller=True)
        return

    target_id, error = await resolve_target(message, users, None if has_reply else target_token)
    if error:
        await send_msg(message, error, media=GM_USAGE_MEDIA, only_caller=True)
        return

    target = await users.add_balance(target_id, amount)
    if target is None:
        await send_msg(message, "Не удалось обновить баланс", media=GM_USAGE_MEDIA, only_caller=True)
        return

    sign = "+" if amount > 0 else ""
    await send_msg(message, text=f"Выдано {sign}{amount}\nID: <code>{target.tg_id}</code>\nБаланс: <b>{target.balance}</b>", media=GM_OK_MEDIA or GM_MEDIA, only_caller=True)
