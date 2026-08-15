from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.service.enum import Role


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

        stmt = (
            insert(User)
            .values(tg_id=tg_id, username=username)
            .returning(User)
        )

        user = stmt.scalar_one()
        return user, True