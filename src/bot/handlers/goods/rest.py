from datetime import date, datetime, timezone

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.bot.handlers.goods.keyboard import kb_rest_confirm
from src.bot.handlers.private.shop.keyboard import kb_shop
from src.database.models import User
from src.database.repositories import CheckRepository, UserRepository
from src.service.errors import UserNotFound
from src.service.logger import log_app, log_fin
from src.service.receipt import send_check_file
from src.service.sendmsg import send_msg
from src.service.vault.goods import GOODS, Goods, get_goods, rest_cost, rest_weeks
from src.service.vault.texts import (
    ERR_NO_MONEY,
    REST_ASK_DATE,
    REST_BAD_DATE,
    REST_CANCELLED,
    REST_NO_EXTEND,
    REST_PAST_DATE,
    SHOP_TITLE,
    txt_no_money,
    txt_rest_confirm,
    txt_rest_ok,
)

router = Router(name="rest")


class RestBuy(StatesGroup):
    date = State()
    confirm = State()


@router.callback_query(F.data == f"shop_buy:{Goods.REST}", F.message.chat.type == "private")
async def clbck_shop_buy_rest(callback: CallbackQuery, user: User, users: UserRepository, state: FSMContext):
    log_app.info("rest buy start tg_id={}", callback.from_user.id)
    await state.set_state(RestBuy.date)
    await send_msg(callback.message, REST_ASK_DATE, edit=True)
    await callback.answer()


@router.message(RestBuy.date, F.chat.type == "private")
async def msg_rest_date(message: Message, user: User, users: UserRepository, state: FSMContext):
    log_app.info("rest date input tg_id={}", message.from_user.id)
    raw = (message.text or "").strip()

    try:
        until = datetime.strptime(raw, "%d.%m.%Y").date()
    except ValueError:
        log_app.warning("rest bad date tg_id={} raw={}", message.from_user.id, raw)
        await send_msg(message, REST_BAD_DATE)
        return

    today = datetime.now(timezone.utc).date()

    if until < today:
        log_app.warning("rest past date tg_id={} raw={}", message.from_user.id, raw)
        await send_msg(message, REST_PAST_DATE)
        return

    current = user.rest_until
    weeks = rest_weeks(until, current)
    cost = rest_cost(until, current)

    if weeks <= 0:
        await send_msg(message, REST_NO_EXTEND)
        return

    enough = await users.check_money(user, cost)

    if not enough:
        log_app.warning("rest no money tg_id={} cost={} balance={}", user.tg_id, cost, user.balance)
        await state.clear()
        await send_msg(message, txt_no_money(cost, user.balance))
        return

    await state.update_data(until=until.isoformat(), cost=cost, weeks=weeks, raw=raw)
    await state.set_state(RestBuy.confirm)
    cur_str = current.strftime("%d.%m.%Y") if current and current >= today else None
    await send_msg(message, txt_rest_confirm(raw, weeks, cost, user.balance, cur_str), reply_markup=kb_rest_confirm())


@router.callback_query(StateFilter(RestBuy.confirm), F.data == "rest_confirm:yes", F.message.chat.type == "private")
async def clbck_rest_yes(callback: CallbackQuery, user: User, users: UserRepository, checks: CheckRepository, state: FSMContext):
    data = await state.get_data()
    until = date.fromisoformat(data["until"])
    cost = int(data["cost"])
    weeks = int(data["weeks"])
    raw = data["raw"]

    weeks2 = rest_weeks(until, user.rest_until)
    cost2 = rest_cost(until, user.rest_until)

    if weeks2 <= 0:
        await state.clear()
        await callback.answer(REST_NO_EXTEND, show_alert=True)
        return

    cost, weeks = cost2, weeks2

    if not await users.check_money(user, cost):
        await state.clear()
        await callback.answer(ERR_NO_MONEY, show_alert=True)
        await send_msg(callback.message, txt_no_money(cost, user.balance), edit=True)
        return

    try:
        updated = await users.add_balance(user.tg_id, -cost)
    except UserNotFound:
        log_app.error("rest charge UserNotFound tg_id={}", user.tg_id)
        await state.clear()
        await callback.answer(ERR_NO_MONEY, show_alert=True)
        return

    try:
        await users.set_rest(user.tg_id, until)
    except UserNotFound:
        log_fin.warning("rest refund tg_id={} cost={}", user.tg_id, cost)

        try:
            await users.add_balance(user.tg_id, cost)
        except UserNotFound:
            log_app.error("rest refund failed UserNotFound tg_id={}", user.tg_id)

        await state.clear()
        await callback.answer(ERR_NO_MONEY, show_alert=True)
        return

    await state.clear()
    log_app.info("rest bought tg_id={} until={} cost={} weeks={}", user.tg_id, until, cost, weeks)
    balance = updated.balance
    check = await checks.create(
        user_tg_id=user.tg_id,
        good_id=Goods.REST,
        good_title=GOODS[Goods.REST]["title"],
        amount=cost,
        balance_after=balance,
        qty=1,
        meta={"weeks": weeks, "rest_until": raw},
    )
    await send_msg(callback.message, txt_rest_ok(raw, weeks, cost, balance), edit=True)
    await send_check_file(callback.message, check)
    await send_msg(callback.message, SHOP_TITLE, reply_markup=kb_shop(get_goods(), 0))
    await callback.answer()


@router.callback_query(StateFilter(RestBuy.confirm), F.data == "rest_confirm:no", F.message.chat.type == "private")
async def clbck_rest_no(callback: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    await send_msg(callback.message, REST_CANCELLED, reply_markup=kb_shop(get_goods(), 0), edit=True)
    await callback.answer()
