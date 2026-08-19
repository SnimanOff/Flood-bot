from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.handlers.private.shop.keyboard import kb_shop
from src.database.models import User
from src.database.repositories import CheckRepository, UserRepository
from src.service.errors import UserNotFound
from src.service.logger import log_app, log_fin
from src.service.receipt import send_check_file
from src.service.sendmsg import send_msg
from src.service.vault.goods import GOODS, Goods, get_goods
from src.service.vault.texts import ERR_NO_MONEY, SHOP_TITLE, txt_purge_ok

router = Router(name="purge_immunity")


@router.callback_query(F.data == f"shop_buy:{Goods.PURGE_IMMUNITY}", F.message.chat.type == "private")
async def clbck_shop_buy_purge(callback: CallbackQuery, user: User, users: UserRepository, checks: CheckRepository):
    good = GOODS[Goods.PURGE_IMMUNITY]
    cost = int(good["price"])
    log_app.info("purge buy start tg_id={} cost={}", user.tg_id, cost)

    if not await users.check_money(user, cost):
        log_app.warning("purge no money tg_id={} cost={} balance={}", user.tg_id, cost, user.balance)
        await callback.answer(ERR_NO_MONEY, show_alert=True)
        return

    try:
        updated = await users.add_balance(user.tg_id, -cost)
    except UserNotFound:
        log_app.error("purge charge UserNotFound tg_id={}", user.tg_id)
        await callback.answer(ERR_NO_MONEY, show_alert=True)
        return

    try:
        updated = await users.add_inventory(user.tg_id, str(Goods.PURGE_IMMUNITY), 1)
    except UserNotFound:
        log_fin.warning("purge refund tg_id={} cost={}", user.tg_id, cost)
        try:
            await users.add_balance(user.tg_id, cost)
        except UserNotFound:
            log_app.error("purge refund failed UserNotFound tg_id={}", user.tg_id)
        await callback.answer(ERR_NO_MONEY, show_alert=True)
        return

    qty = (updated.inventory or {}).get(str(Goods.PURGE_IMMUNITY), 1)
    check = await checks.create(
        user_tg_id=user.tg_id,
        good_id=str(Goods.PURGE_IMMUNITY),
        good_title=good["title"],
        amount=cost,
        balance_after=updated.balance,
        qty=1,
        meta={"inventory_total": qty},
    )
    await send_msg(callback.message, txt_purge_ok(good["title"], cost, updated.balance, qty))
    await send_check_file(callback.message, check)
    await send_msg(callback.message, SHOP_TITLE, reply_markup=kb_shop(get_goods(), 0), edit=True)
    await callback.answer()
    log_app.info("purge bought tg_id={} cost={}", user.tg_id, cost)
