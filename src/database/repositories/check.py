from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Check
from src.service.logger import log_fin, log_tech


class CheckRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_tg_id: int, good_id: str, good_title: str, amount: int, balance_after: int, qty: int = 1, meta: dict | None = None) -> Check:
        check = Check(
            user_tg_id=user_tg_id,
            good_id=good_id,
            good_title=good_title,
            amount=amount,
            qty=qty,
            balance_after=balance_after,
            meta=meta or {},
        )
        self._session.add(check)
        await self._session.flush()
        log_fin.info("check created id={} tg_id={} good={} amount={}", check.id, user_tg_id, good_id, amount)
        return check

    async def get(self, check_id: int) -> Check | None:
        stmt = await self._session.execute(select(Check).where(Check.id == check_id))
        check = stmt.scalar_one_or_none()
        if check is None:
            log_tech.debug("check get not found id={}", check_id)
        else:
            log_tech.debug("check get id={} good={}", check_id, check.good_id)
        return check
