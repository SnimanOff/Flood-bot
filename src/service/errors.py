class AppError(Exception):
    """Domain error base."""


class UserNotFound(AppError):
    def __init__(self, tg_id: int | None = None):
        self.tg_id = tg_id
        super().__init__(f"user not found tg_id={tg_id}")


class NotEnoughMoney(AppError):
    def __init__(self, needed: int, balance: int):
        self.needed = needed
        self.balance = balance
        super().__init__(f"not enough money needed={needed} balance={balance}")


class MoneyRequestNotFound(AppError):
    def __init__(self, request_id: int):
        self.request_id = request_id
        super().__init__(f"money request not found id={request_id}")


class MoneyRequestAlreadyResolved(AppError):
    def __init__(self, request_id: int, status: str):
        self.request_id = request_id
        self.status = status
        super().__init__(f"money request already resolved id={request_id} status={status}")


class GoodUnavailable(AppError):
    def __init__(self, good_id: str):
        self.good_id = good_id
        super().__init__(f"good unavailable id={good_id}")


class PermissionDenied(AppError):
    def __init__(self, detail: str = "permission denied"):
        super().__init__(detail)


class NotEnoughInventory(AppError):
    def __init__(self, tg_id: int, good_id: str, needed: int = 1):
        self.tg_id = tg_id
        self.good_id = good_id
        self.needed = needed
        super().__init__(f"not enough inventory tg_id={tg_id} good={good_id}")
