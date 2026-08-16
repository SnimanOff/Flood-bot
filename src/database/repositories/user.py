from sqlalchemy import select, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from service.vault.roles import Role

from datetime import datetime, timezone, timedelta

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

        stmt = await self._session.execute(
            insert(User).values(tg_id=tg_id, username=username).returning(User)
        )
        user = stmt.scalar_one()
        return user, True

    async def get_by_username(self, username: str) -> User | None:
        name = username.lstrip("@").lower()
        stmt = await self._session.execute(select(User).where(User.username.ilike(name)))
        return stmt.scalar_one_or_none()

    async def add_balance(self, tg_id: int, amount: int) -> User | None:
        user = await self.get_by_tg_id(tg_id)
        if user is None:
            return None
        user.balance += amount
        await self._session.flush()
        return user

    async def is_banned(self, tg_id: int) -> bool:
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            return False

        if user.banned_until == None or user.banned_until < datetime.now(timezone.utc):
            return False
        
        return True
    
    async def get_owners(self) -> list[User]:
        now = datetime.now(timezone.utc)

        stmt = await self._session.execute(
            select(User)
            .where(
                User.role >= Role.OWNER,
                or_(User.banned_until.is_(None), 
                User.banned_until < now),
            )
        )
        return list(stmt.scalars().all())

    async def set_last_query_money(self, tg_id: int, when: datetime | None = None) -> User | None:
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            return None
        
        user.last_query_money = when or datetime.now(timezone.utc)
        
        await self._session.flush()
        return user

    def cd_left(self, user: User) -> timedelta | None:

        if user.last_query_money is None:
            return None
        
        last = user.last_query_money

        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)

        ends = last + timedelta(hours=24)
        left = ends - datetime.now(timezone.utc)

        if left.total_seconds() <= 0:
            return None
        
        return left