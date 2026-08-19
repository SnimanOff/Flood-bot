# ---------------- common ----------------
ERR_NO_RIGHTS = "Недостаточно прав"
ERR_NO_MONEY = "Недостаточно средств"
ERR_ALREADY = "Уже обработано"
ERR_USER_NOT_FOUND = "Пользователь не найден"


def txt_no_money(needed: int, balance: int) -> str:
    return f"Недостаточно средств\nНужно: <b>{needed}</b>\nБаланс: <b>{balance}</b>"


def txt_page(cur, total) -> str:
    return f"Страница {cur} из {total}"


# ---------------- start ----------------
def txt_start_hello(name: str, version: str, updated: str, balance: int) -> str:
    return (
        f"Привет, {name}!\n"
        f"\n"
        f"Баланс: <b>{balance}</b>\n"
        f"\n"
        f"Версия: <code>v{version}</code>\n"
        f"Последнее обновление: {updated}"
    )


# ---------------- help ----------------
HELP_INLINE_TITLE = "Справка"


def txt_help_body() -> str:
    from src.service.vault.version import get_cached_version
    ver = get_cached_version()
    return (
        f"<b>Справка</b> <code>v{ver}</code>\n"
        f"\n"
        f"<b>Для всех</b>\n"
        f"/start - меню в личке\n"
        f"/help - эта справка\n"
        f"/rests - кто на ресте\n"
        f"\n"
        f"<b>влд</b>\n"
        f"/gm id сумма - выдать валюту\n"
        f"  /gm 123456 100\n"
        f"  reply: /gm 100\n"
        f"/setrest id ДД.ММ.ГГГГ - выдать рест\n"
        f"  /setrest 123456 25.12.2027\n"
        f"  reply: /setrest 25.12.2027\n"
        f"/unpurge - снять пощаду\n"
        f"\n"
        f"<b>рут</b>\n"
        f"/setrole id роль - user/moderator/admin/owner/root\n"
        f"  /setrole 123456 owner\n"
        f"\n"
        f"<b>Личка</b>\n"
        f"Магазин, пополнить, мои награды - после /start\n"
        f"\n"
        f"<b>Группа</b>\n"
        f"Пиши команды: /gm /setrest /unpurge /setrole\n"
        f"Ответ виден только тебе\n"
        f"/rests - список рестов"
    )


# ---------------- shop ----------------
SHOP_TITLE = "Магазин"
SHOP_UNAVAILABLE = "Товар недоступен"


def txt_good_card(good: dict) -> str:
    return (
        f"<b>{good['title']}</b>\n"
        f"Цена: <b>{good['price']}</b>\n"
        f"\n"
        f"{good['description']}"
    )


# ---------------- balance ----------------
BALANCE_ASK_AMOUNT = "Введите сумму (целое число):"
BALANCE_NEED_INT = "Введите целое число"
BALANCE_NEED_POSITIVE = "Сумма должна быть больше 0"
BALANCE_ASK_PROOF = "Пришлите текст заявки или одно фото с подписью"
BALANCE_SENT = "Заявка отправлена"
BALANCE_STATUS_OK = "\n\nПринято"
BALANCE_STATUS_NO = "\n\nОтказано"
BALANCE_PROFILE = "профиль"


def txt_cd_hm(hours, minutes) -> str:
    return f"{hours}ч {minutes}м"


def txt_cd_ms(minutes, seconds) -> str:
    return f"{minutes}м {seconds}с"


def txt_cd_s(seconds) -> str:
    return f"{seconds}с"


def txt_balance_cd(left_str: str) -> str:
    return f"Подождите ещё {left_str}"


def txt_balance_admin(tg_id, user_link, amount, caption_text) -> str:
    return (
        f"От кого:\n"
        f"ID: <code>{tg_id}</code>\n"
        f"{user_link}\n"
        f"Сумма: <b>{amount}</b>\n"
        f"Текст: {caption_text}"
    )


def txt_balance_user_ok(amount) -> str:
    return f"Заявка на <b>{amount}</b> принята"


def txt_balance_user_no(amount) -> str:
    return f"Заявка на <b>{amount}</b> отклонена"


# ---------------- gm ----------------
GM_USAGE = "Использование:\n/gm <id|@user> <сумма>\nили reply: /gm <сумма>"
GM_BAD_AMOUNT = "Сумма должна быть целым числом ≠ 0"
GM_UPDATE_FAIL = "Не удалось обновить баланс"
GM_NEED_TARGET = "Укажи пользователя: reply или /gm <id|@user> <сумма>"
GM_USER_NOT_FOUND = "Пользователь не найден в БД (нужен id или чтобы он писал боту)"


def txt_gm_ok(sign, amount, tg_id, balance) -> str:
    return f"Выдано {sign}{amount}\nID: <code>{tg_id}</code>\nБаланс: <b>{balance}</b>"


# ---------------- rest ----------------
REST_ASK_DATE = "Введите дату окончания реста (ДД.ММ.ГГГГ):"
REST_BAD_DATE = "Формат: ДД.ММ.ГГГГ"
REST_PAST_DATE = "Дата не может быть в прошлом"
REST_NO_EXTEND = "Дата не позже текущего реста"
REST_CANCELLED = "Покупка отменена"


def txt_rest_confirm(until_str: str, weeks: int, cost: int, balance: int, current_rest_str: str | None) -> str:
    lines = ['<b>Подтверждение покупки реста</b>', ""]
    if current_rest_str:
        lines.append(f"Сейчас до: <b>{current_rest_str}</b>")
    lines.append(f"Новая дата: <b>{until_str}</b>")
    lines.append(f"Доплата недель: <b>{weeks}</b>")
    lines.append(f"К оплате: <b>{cost}</b>")
    lines.append(f"Баланс: <b>{balance}</b>")
    return "\n".join(lines)


def txt_rest_ok(date_str: str, weeks: int, cost: int, balance: int) -> str:
    return f"Рест до <b>{date_str}</b>\nНедель: <b>{weeks}</b>\nСписано: <b>{cost}</b>\nБаланс: <b>{balance}</b>"


# ---------------- purge ----------------
def txt_purge_ok(title: str, cost: int, balance: int, qty: int) -> str:
    return f"Куплено: <b>{title}</b>\nСписано: <b>{cost}</b>\nВ инвентаре: <b>{qty}</b>\nБаланс: <b>{balance}</b>"


# ---------------- checks ----------------
def txt_check_caption(check_id: int) -> str:
    return f"Чек №{check_id}"


# ---------------- rests ----------------
RESTS_EMPTY = "Активных рестов нет"
RESTS_INLINE_TITLE = "Активные ресты"


def txt_rests_line(tg_id: int, username: str | None, until_str: str) -> str:
    from html import escape
    if username:
        who = f'<a href="tg://user?id={tg_id}">@{escape(username)}</a>'
    else:
        who = f'<a href="tg://user?id={tg_id}"><code>{tg_id}</code></a>'
    return f"• {who} - <b>{until_str}</b>"


def txt_rests_list(lines: list[str]) -> str:
    if not lines:
        return RESTS_EMPTY
    return "Активные ресты:\n\n" + "\n".join(lines)


# ---------------- unpurge ----------------
UNPURGE_EMPTY = "Ни у кого нет пощады"
UNPURGE_INLINE_TITLE = "Снять пощаду"
UNPURGE_DONE = "Пощада снята"
UNPURGE_FAIL = "Не удалось снять"
UNPURGE_NONE = "У пользователя нет пощады"


def txt_unpurge_header(page: int, total: int, count: int) -> str:
    return f"<b>Пощада на чистке</b>\nВсего: <b>{count}</b>\nСтр. {page + 1}/{total}"


def txt_unpurge_btn(username: str | None, tg_id: int, qty: int) -> str:
    name = f"@{username}" if username else str(tg_id)
    return f"{name} ×{qty}"


def txt_unpurge_ok(tg_id: int, username: str | None, left: int) -> str:
    who = f"@{username}" if username else str(tg_id)
    return f"Снято с <b>{who}</b>\nОсталось: <b>{left}</b>"


# ---------------- my items ----------------
MY_ITEMS_INV_EMPTY = "пусто"
MY_ITEMS_REST_NONE = "нет"


def txt_my_items_inventory_line(title: str, qty: int) -> str:
    return f"• {title} ×<b>{qty}</b>"


def txt_my_items_rest_active(date_str: str) -> str:
    return f"до <b>{date_str}</b>"


def txt_my_items(inv_block: str, rest_block: str) -> str:
    return (
        f"<b>Инвентарь</b>\n{inv_block}\n"
        f"\n"
        f"<b>Рест</b>\n{rest_block}"
    )

# ---------------- setrest ----------------
SETREST_INLINE_TITLE = "Установить рест"
SETREST_USAGE = "Без второго @:\nsetrest id ДД.ММ.ГГГГ\nsetrest username ДД.ММ.ГГГГ\n\nПример:\nsetrest QwertyGeny 25.12.2027\nsetrest 123456789 25.12.2027"
SETREST_NEED_USER = "Укажи id или username (без @)"
SETREST_NEED_DATE = "Укажи дату ДД.ММ.ГГГГ"
SETREST_CMD_USAGE = "Использование:\n/setrest <id|username> ДД.ММ.ГГГГ\nили reply: /setrest ДД.ММ.ГГГГ\nusername без @"
SETREST_BAD_DATE = "Формат даты: ДД.ММ.ГГГГ"
SETREST_PAST = "Дата не может быть в прошлом"
SETREST_USER_NOT_FOUND = "Пользователь не найден"
SETREST_CANCELLED = "Отменено"
SETREST_DONE = "Рест установлен"


def txt_setrest_preview(tg_id: int, username: str | None, until_str: str) -> str:
    from html import escape
    if username:
        who = f"@{escape(username)}"
    else:
        who = f"<code>{tg_id}</code>"
    return (
        f"<b>Установить рест</b>\n"
        f"\n"
        f"Кому: {who}\n"
        f"ID: <code>{tg_id}</code>\n"
        f"До: <b>{until_str}</b>"
    )


def txt_setrest_ok(tg_id: int, username: str | None, until_str: str) -> str:
    from html import escape
    if username:
        who = f"@{escape(username)}"
    else:
        who = f"<code>{tg_id}</code>"
    return (
        f"{SETREST_DONE}\n"
        f"Кому: {who}\n"
        f"ID: <code>{tg_id}</code>\n"
        f"До: <b>{until_str}</b>"
    )


# ---------------- roles ----------------
SETROLE_USAGE = "Использование:\n/setrole <id|@user> <role>\nили reply: /setrole <role>\nРоли: user, moderator, admin, owner, root"
SETROLE_BAD_ROLE = "Неизвестная роль"
SETROLE_LAST_ROOT = "Нельзя снять ROOT: вы последний ROOT"
SETROLE_NEED_TARGET = "Укажи пользователя: reply или /setrole <id|@user> <role>"
SETROLE_USER_NOT_FOUND = "Пользователь не найден в БД (нужен id или чтобы он писал боту)"


def txt_setrole_ok(tg_id: int, role_name: str) -> str:
    return f"Роль обновлена\nID: <code>{tg_id}</code>\nРоль: <b>{role_name}</b>"

