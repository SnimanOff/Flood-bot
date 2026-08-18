# ---------------- start ----------------
def txt_start_hello(name: str) -> str:
    return f"Привет, {name}!"


# ---------------- shop ----------------
SHOP_UNAVAILABLE = "Товар недоступен"


def txt_shop_page(cur, total) -> str:
    return f"Страница {cur} из {total}"


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
BALANCE_NO_RIGHTS = "Недостаточно прав"
BALANCE_ALREADY = "Уже обработано"
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
GM_NO_RIGHTS = "Недостаточно прав"
GM_USAGE = "Использование:\n/gm <id|@user> <сумма>\nили reply: /gm <сумма>"
GM_BAD_AMOUNT = "Сумма должна быть целым числом ≠ 0"
GM_UPDATE_FAIL = "Не удалось обновить баланс"
GM_NEED_TARGET = "Укажи пользователя: reply или /gm <id|@user> <сумма>"
GM_USER_NOT_FOUND = "Пользователь не найден в БД (нужен id или чтобы он писал боту)"


def txt_gm_ok(sign, amount, tg_id, balance) -> str:
    return f"Выдано {sign}{amount}\nID: <code>{tg_id}</code>\nБаланс: <b>{balance}</b>"

# ---------------- rest ----------------
REST_NO_MONEY = "Недостаточно средств"
REST_ASK_DATE = "Введите дату окончания реста (ДД.ММ.ГГГГ):"
REST_BAD_DATE = "Формат: ДД.ММ.ГГГГ"
REST_PAST_DATE = "Дата не может быть в прошлом"


def txt_rest_ok(date_str: str, weeks: int, cost: int, balance: int) -> str:
    return f"Рест до <b>{date_str}</b>\nНедель: <b>{weeks}</b>\nСписано: <b>{cost}</b>\nБаланс: <b>{balance}</b>"


def txt_rest_no_money(needed: int, balance: int) -> str:
    return f"Недостаточно средств\nНужно: <b>{needed}</b>\nБаланс: <b>{balance}</b>"
