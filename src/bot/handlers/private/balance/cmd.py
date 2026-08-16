import json
from datetime import timedelta
from html import escape

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.bot.handlers.private.balance.keyboard import kb_admin_request
from src.database.models import MoneyRequest, User
from src.database.repositories import MoneyRequestRepository, UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.media import BALANCE_ASK_MEDIA, BALANCE_SENT_MEDIA
from src.service.vault.roles import Role

router = Router(name="balance")


class BalanceRequest(StatesGroup):
    amount = State()
    proof = State()


def fmt_cd(left: timedelta) -> str:
    total = int(left.total_seconds())
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)

    if hours:
        return f"{hours}ч {minutes}м"

    if minutes:
        return f"{minutes}м {seconds}с"

    return f"{seconds}с"


async def edit_message_content(callback_message, text, reply_markup=None):
    if callback_message.photo:
        await callback_message.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        await callback_message.edit_text(text=text, reply_markup=reply_markup)


async def update_admin_messages(bot: Bot, request: MoneyRequest, status_line: str):
    text = request.caption + status_line
    notifies = json.loads(request.notifies or "[]")
    for item in notifies:
        try:
            if request.photo_file_id:
                await bot.edit_message_caption(chat_id=item["chat_id"], message_id=item["message_id"], caption=text, parse_mode="HTML", reply_markup=None)
            else:
                await bot.edit_message_text(chat_id=item["chat_id"], message_id=item["message_id"], text=text, parse_mode="HTML", reply_markup=None)
        except Exception:
            pass

# ---------------- запрос средств ----------------

@router.callback_query(F.data == "start_get_balance", F.message.chat.type == "private")
async def clbck_start_get_balance(callback: CallbackQuery, user: User, users: UserRepository, state: FSMContext):
    left = users.cd_left(user)
    if left is not None:
        await callback.answer(f"Подождите ещё {fmt_cd(left)}", show_alert=True)
        return

    await state.set_state(BalanceRequest.amount)
    await edit_message_content(callback.message, "Введите сумму (целое число):", reply_markup=None)
    await callback.answer()

@router.message(BalanceRequest.amount, F.chat.type == "private")
async def msg_balance_amount(message: Message, user: User, users: UserRepository, state: FSMContext):
    raw = (message.text or "").strip()

    try:
        amount = int(raw)
    except ValueError:
        await send_msg(message, "Введите целое число", media=BALANCE_ASK_MEDIA)
        return

    if amount <= 0:
        await send_msg(message, "Сумма должна быть больше 0", media=BALANCE_ASK_MEDIA)
        return

    left = users.cd_left(user)
    if left is not None:
        await state.clear()
        await send_msg(message, f"Подождите ещё {fmt_cd(left)}", media=BALANCE_ASK_MEDIA)
        return

    await state.update_data(amount=amount)
    await state.set_state(BalanceRequest.proof)
    await send_msg(message, "Пришлите текст заявки или одно фото с подписью", media=BALANCE_ASK_MEDIA)

@router.message(BalanceRequest.proof, F.chat.type == "private")
async def msg_balance_proof(message: Message, user: User, users: UserRepository, money_requests: MoneyRequestRepository, state: FSMContext, bot: Bot):
    if message.photo:
        file_id = message.photo[-1].file_id
        text = message.caption or ""
    elif message.text:
        file_id = None
        text = message.text
    else:
        await send_msg(message, "Пришлите текст заявки или одно фото с подписью", media=BALANCE_ASK_MEDIA)
        return

    data = await state.get_data()
    amount = data.get("amount")
    if amount is None:
        await state.clear()
        await send_msg(message, "Введите сумму (целое число):", media=BALANCE_ASK_MEDIA)
        return

    left = users.cd_left(user)
    if left is not None:
        await state.clear()
        await send_msg(message, f"Подождите ещё {fmt_cd(left)}", media=BALANCE_ASK_MEDIA)
        return

    await users.set_last_query_money(user.tg_id)
    await state.clear()

    tg_id = message.from_user.id
    if message.from_user.username:
        user_link = f'<a href="tg://user?id={tg_id}">@{escape(message.from_user.username)}</a>'
    else:
        user_link = f'<a href="tg://user?id={tg_id}">профиль</a>'

    caption_text = escape(text) if text else "—"
    admin_text = (
        f"От кого:\n"
        f"ID: <code>{tg_id}</code>\n"
        f"{user_link}\n"
        f"Сумма: <b>{amount}</b>\n"
        f"Текст: {caption_text}"
    )

    req = await money_requests.create(
        user_tg_id=tg_id,
        amount=amount,
        caption=admin_text,
        photo_file_id=file_id,
    )

    notifies: list[dict] = []
    owners = await users.get_owners()
    for owner in owners:
        try:
            if file_id:
                msg = await bot.send_photo(
                    owner.tg_id,
                    photo=file_id,
                    caption=admin_text,
                    parse_mode="HTML",
                    reply_markup=kb_admin_request(req.id),
                )
            else:
                msg = await bot.send_message(
                    owner.tg_id,
                    text=admin_text,
                    parse_mode="HTML",
                    reply_markup=kb_admin_request(req.id),
                )
            notifies.append({"chat_id": msg.chat.id, "message_id": msg.message_id})
        except Exception:
            pass

    await money_requests.set_notifies(req.id, notifies)

    await send_msg(message, "Заявка отправлена", media=BALANCE_SENT_MEDIA)

# ---------------- решение админа ----------------

@router.callback_query(F.data.startswith("bal_ok:"), F.message.chat.type == "private")
async def clbck_bal_ok(callback: CallbackQuery, user: User, users: UserRepository, money_requests: MoneyRequestRepository, bot: Bot):
    if user.role < Role.OWNER:
        await callback.answer("Недостаточно прав", show_alert=True)
        return

    parts = callback.data.split(":")
    request_id = int(parts[1])

    req = await money_requests.resolve(request_id, "ok")
    if req is None:
        await callback.answer("Уже обработано", show_alert=True)
        return

    await users.add_balance(req.user_tg_id, req.amount)
    await update_admin_messages(bot, req, "\n\nПринято")

    try:
        await bot.send_message(req.user_tg_id, f"Заявка на <b>{req.amount}</b> принята", parse_mode="HTML")
    except Exception:
        pass

    await callback.answer()

@router.callback_query(F.data.startswith("bal_no:"), F.message.chat.type == "private")
async def clbck_bal_no(callback: CallbackQuery, user: User, users: UserRepository, money_requests: MoneyRequestRepository, bot: Bot):
    if user.role < Role.OWNER:
        await callback.answer("Недостаточно прав", show_alert=True)
        return

    parts = callback.data.split(":")
    request_id = int(parts[1])

    req = await money_requests.resolve(request_id, "no")
    if req is None:
        await callback.answer("Уже обработано", show_alert=True)
        return

    await update_admin_messages(bot, req, "\n\nОтказано")

    try:
        await bot.send_message(req.user_tg_id, f"Заявка на <b>{req.amount}</b> отклонена", parse_mode="HTML")
    except Exception:
        pass

    await callback.answer()
