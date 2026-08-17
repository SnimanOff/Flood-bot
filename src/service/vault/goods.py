from enum import StrEnum


class Goods(StrEnum):
    REST = "rest"
    PURGE_IMMUNITY = "purge_immunity"


GOODS: dict[str, dict] = {
    Goods.REST: {
        "id": Goods.REST,
        "title": "Продление реста",
        "description": "Продлевает рест.",
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
