from enum import StrEnum
import math
from datetime import date, datetime, timezone


class Goods(StrEnum):
    REST = "rest"
    PURGE_IMMUNITY = "purge_immunity"


GOODS: dict[str, dict] = {
    Goods.REST: {
        "id": Goods.REST,
        "title": "Продление реста",
        "description": "Продлевает рест. Цена указана за 1 неделю реста.",
        "price": 100,
        "active": True,
        "media": "",
    },
    Goods.PURGE_IMMUNITY: {
        "id": Goods.PURGE_IMMUNITY,
        "title": "Пощада на чистке",
        "description": "Иммунитет к чистке.",
        "price": 200,
        "active": True,
        "media": "",
    },
}


def get_goods() -> list[dict]:
    return [item for item in GOODS.values() if item.get("active", True)]


def get_good(good_id: str) -> dict | None:
    return GOODS.get(good_id)


def rest_start_date(current_rest: date | None = None) -> date:
    today = datetime.now(timezone.utc).date()
    if current_rest is not None and current_rest >= today:
        return current_rest
    return today


def rest_weeks(until: date, current_rest: date | None = None) -> int:
    start = rest_start_date(current_rest)
    days = (until - start).days
    if days <= 0:
        return 0
    return max(1, math.ceil(days / 7))


def rest_cost(until: date, current_rest: date | None = None) -> int:
    weeks = rest_weeks(until, current_rest)
    return int(weeks * int(GOODS[Goods.REST]["price"]))
