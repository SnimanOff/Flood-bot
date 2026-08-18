import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import MoneyRequest
from src.service.errors import MoneyRequestAlreadyResolved, MoneyRequestNotFound
from src.service.logger import log_fin, log_tech


class MoneyRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_tg_id: int, amount: int, caption: str, photo_file_id: str | None = None) -> MoneyRequest:
        req = MoneyRequest(
            user_tg_id=user_tg_id,
            amount=amount,
            caption=caption,
            photo_file_id=photo_file_id,
            status="pending",
            notifies="[]",
        )

        self._session.add(req)
        await self._session.flush()
        log_fin.info("money request created id={} amount={} user_tg_id={}", req.id, amount, user_tg_id)
        return req

    async def get(self, request_id: int) -> MoneyRequest | None:
        stmt = await self._session.execute(
            select(MoneyRequest)
            .where(MoneyRequest.id == request_id)
        )
        req = stmt.scalar_one_or_none()
        if req is None:
            log_tech.debug("money request get not found id={}", request_id)
        else:
            log_tech.debug("money request get id={} status={}", request_id, req.status)
        return req

    async def set_notifies(self, request_id: int, notifies: list[dict]) -> MoneyRequest:
        req = await self.get(request_id)

        if req is None:
            raise MoneyRequestNotFound(request_id)

        req.notifies = json.dumps(notifies)
        await self._session.flush()
        log_tech.debug("money request set_notifies id={} count={}", request_id, len(notifies))
        return req

    async def resolve(self, request_id: int, status: str) -> MoneyRequest:
        req = await self.get(request_id)

        if req is None:
            raise MoneyRequestNotFound(request_id)

        if req.status != "pending":
            raise MoneyRequestAlreadyResolved(request_id, req.status)

        req.status = status
        await self._session.flush()
        log_fin.info("money request resolved id={} status={} user_tg_id={} amount={}", request_id, status, req.user_tg_id, req.amount)
        return req
