from sqlalchemy import select, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.service.vault.roles import Role

from datetime import datetime, timezone, timedelta, date

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        """
        Метод получения юзера по его tg_id
        """
        stmt = await self._session.execute(
            select(User)
            .where(User.tg_id == tg_id)
        )

        return stmt.scalar_one_or_none()

    async def get_or_create(self, tg_id: int, username: str | None = None) -> tuple[User, bool]:
        """
        Метод получения/создания юзера по tg_id. Возвращает объект юзера
        """
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
        """
        Метод получения юзера по его username
        """
        name = username.lstrip("@").lower()
        stmt = await self._session.execute(select(User).where(User.username.ilike(name)))
        return stmt.scalar_one_or_none()

    async def add_balance(self, tg_id: int, amount: int) -> User | None:
        """
        Метод добавления баланса по tg_id. Может использоваться для списания
        """
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            return None
        
        user.balance += amount
        await self._session.flush()
        return user

    async def is_banned(self, tg_id: int) -> bool:
        """
        Метод проверки пользователя на бан по его tg_id
        """
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            return False

        if user.banned_until == None or user.banned_until < datetime.now(timezone.utc):
            return False
        
        return True
    
    async def get_owners(self) -> list[User]:
        """
        Метод для получения листа id всех OWNER
        """
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
        """
        Метод для установки кулдауна запроса денег
        """
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            return None
        
        user.last_query_money = when or datetime.now(timezone.utc)
        
        await self._session.flush()
        return user

    def cd_left(self, user: User) -> timedelta | None:
        """
        Метод проверки количества оставшегося времени до возможности запросить деньги
        """

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

    async def check_money(self, user: User, needed: int) -> bool:
        """
        Метод для получения информации, хватает ли у пользователя средств
        """

        return user.balance >= needed

    async def set_rest(self, tg_id: int, until: date) -> bool:
        """
        Метод установки реста пользователю
        """
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            return False

        user.rest_until = until
        await self._session.flush()
        return True

    async def get_active_rests(self) -> list[User]:
        """
        Метод получения пользователей с активным рестом
        """
        today = datetime.now(timezone.utc).date()
        stmt = await self._session.execute(select(User).where(User.rest_until.is_not(None)))
        rows = list(stmt.scalars().all())
        active: list[User] = []
        for u in rows:
            if u.rest_until is None:
                continue
            if u.rest_until < today:
                u.rest_until = None
            else:
                active.append(u)
        await self._session.flush()
        active.sort(key=lambda u: u.rest_until or today)
        return active
