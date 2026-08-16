from enum import StrEnum


class Goods(StrEnum):
    REST = "rest"
    PURGE_IMMUNITY = "purge_immunity"

def get_goods():
    goods = []

    for good in Goods:
        goods.append(good)

    return goods