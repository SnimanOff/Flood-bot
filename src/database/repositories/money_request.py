import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import MoneyRequest


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
        return req

    async def get(self, request_id: int) -> MoneyRequest | None:
        stmt = await self._session.execute(
            select(MoneyRequest)
            .where(MoneyRequest.id == request_id)
        )
        return stmt.scalar_one_or_none()

    async def set_notifies(self, request_id: int, notifies: list[dict]) -> MoneyRequest | None:
        req = await self.get(request_id)
        if req is None:
            return None
        req.notifies = json.dumps(notifies)
        await self._session.flush()
        return req

    async def resolve(self, request_id: int, status: str) -> MoneyRequest | None:
        req = await self.get(request_id)
        if req is None or req.status != "pending":
            return None
        req.status = status
        await self._session.flush()
        return req
