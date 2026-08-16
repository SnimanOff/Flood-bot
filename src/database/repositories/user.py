from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from service.vault.roles import Role


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        stmt = await self._session.execute(
            select(User)
            .where(User.tg_id == tg_id)
        )

        return stmt.scalar_one_or_none()

    async def get_or_create(self, tg_id: int, username: str | None = None) -> tuple[User, bool]:
        user = await self.get_by_tg_id(tg_id)

        if user is not None:
            if username is not None and user.username != username:
                user.username = username

            return user, False

        result = await self._session.execute(
            insert(User).values(tg_id=tg_id, username=username).returning(User)
        )
        user = result.scalar_one()
        return user, True

    async def get_by_username(self, username: str) -> User | None:
        name = username.lstrip("@").lower()
        result = await self._session.execute(select(User).where(User.username.ilike(name)))
        return result.scalar_one_or_none()

    async def add_balance(self, tg_id: int, amount: int) -> User | None:
        user = await self.get_by_tg_id(tg_id)
        if user is None:
            return None
        user.balance += amount
        await self._session.flush()
        return user
