from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.database.models import User
from src.database.repositories import UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.goods import Goods, rest_cost, rest_weeks
from src.service.vault.texts import (
    REST_ASK_DATE,
    REST_BAD_DATE,
    REST_NO_MONEY,
    REST_PAST_DATE,
    txt_rest_no_money,
    txt_rest_ok,
)

router = Router(name="rest")


class RestBuy(StatesGroup):
    date = State()


@router.callback_query(F.data == f"shop_buy:{Goods.REST}", F.message.chat.type == "private")
async def clbck_shop_buy_rest(callback: CallbackQuery, user: User, users: UserRepository, state: FSMContext):
    await state.set_state(RestBuy.date)
    await send_msg(callback.message, REST_ASK_DATE, edit=True)
    await callback.answer()


@router.message(RestBuy.date, F.chat.type == "private")
async def msg_rest_date(message: Message, user: User, users: UserRepository, state: FSMContext):
    raw = (message.text or "").strip()

    try:
        until = datetime.strptime(raw, "%d.%m.%Y").date()
    except ValueError:
        await send_msg(message, REST_BAD_DATE)
        return

    if until < datetime.now(timezone.utc).date():
        await send_msg(message, REST_PAST_DATE)
        return

    weeks = rest_weeks(until)
    cost = rest_cost(until)

    enough = await users.check_money(user, cost)

    if not enough:
        await state.clear()
        await send_msg(message, txt_rest_no_money(cost, user.balance))
        return

    updated = await users.add_balance(user.tg_id, -cost)
    ok = await users.set_rest(user.tg_id, until)
    await state.clear()

    if not ok:
        await users.add_balance(user.tg_id, cost)
        await send_msg(message, REST_NO_MONEY)
        return

    balance = updated.balance if updated else user.balance - cost
    await send_msg(message, txt_rest_ok(raw, weeks, cost, balance))