from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.database.models import User
from src.database.repositories import UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.goods import GOODS, Goods
from src.service.vault.texts import (
    REST_ASK_DATE,
    REST_BAD_DATE,
    REST_NO_MONEY,
    REST_PAST_DATE,
    txt_rest_ok,
)

router = Router(name="rest")


class RestBuy(StatesGroup):
    date = State()


@router.callback_query(F.data == f"shop_buy:{Goods.REST}", F.message.chat.type == "private")
async def clbck_shop_buy_rest(callback: CallbackQuery, user: User, users: UserRepository, state: FSMContext):
    rest_cost = GOODS[Goods.REST]["price"]

    enough = await users.check_money(user, rest_cost)

    if not enough:
        await callback.answer(REST_NO_MONEY, show_alert=True)
        return

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

    rest_cost = GOODS[Goods.REST]["price"]

    enough = await users.check_money(user, rest_cost)
    
    if not enough:
        await state.clear()
        await send_msg(message, REST_NO_MONEY)
        return

    updated = await users.add_balance(user.tg_id, -rest_cost)
    ok = await users.set_rest(user.tg_id, until)
    await state.clear()

    if not ok:
        await users.add_balance(user.tg_id, rest_cost)
        await send_msg(message, REST_NO_MONEY)
        return

    balance = updated.balance if updated else user.balance - rest_cost
    await send_msg(message, txt_rest_ok(raw, balance))
