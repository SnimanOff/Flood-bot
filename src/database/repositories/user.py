from datetime import datetime, timezone, timedelta, date

from sqlalchemy import select, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.service.errors import UserNotFound
from src.service.logger import log_app, log_fin, log_tech
from src.service.vault.roles import Role


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
        user = stmt.scalar_one_or_none()
        if user is None:
            log_tech.debug("get_by_tg_id not found tg_id={}", tg_id)
        else:
            log_tech.debug("get_by_tg_id found tg_id={}", tg_id)
        return user

    async def get_or_create(self, tg_id: int, username: str | None = None) -> tuple[User, bool]:
        """
        Метод получения/создания юзера по tg_id. Возвращает объект юзера
        """
        user = await self.get_by_tg_id(tg_id)

        if user is not None:
            if username is not None and user.username != username:
                user.username = username
            log_tech.debug("get_or_create found tg_id={}", tg_id)
            return user, False

        stmt = await self._session.execute(
            insert(User).values(tg_id=tg_id, username=username).returning(User)
        )
        user = stmt.scalar_one()
        log_tech.debug("get_or_create created tg_id={}", tg_id)
        log_app.info("user created tg_id={}", tg_id)
        return user, True

    async def get_by_username(self, username: str) -> User | None:
        """
        Метод получения юзера по его username
        """
        name = username.lstrip("@").lower()
        stmt = await self._session.execute(select(User).where(User.username.ilike(name)))
        user = stmt.scalar_one_or_none()
        if user is None:
            log_tech.debug("get_by_username not found username={}", name)
        else:
            log_tech.debug("get_by_username found username={} tg_id={}", name, user.tg_id)
        return user

    async def add_balance(self, tg_id: int, amount: int) -> User:
        """
        Метод добавления баланса по tg_id. Может использоваться для списания
        """
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            raise UserNotFound(tg_id)

        before = user.balance
        user.balance += amount
        await self._session.flush()
        log_fin.info("balance change tg_id={} delta={} balance={}->{}", tg_id, amount, before, user.balance)
        return user

    async def is_banned(self, tg_id: int) -> bool:
        """
        Метод проверки пользователя на бан по его tg_id
        """
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            log_tech.debug("is_banned tg_id={} -> False (no user)", tg_id)
            return False

        if user.banned_until == None or user.banned_until < datetime.now(timezone.utc):
            log_tech.debug("is_banned tg_id={} -> False", tg_id)
            return False

        log_tech.debug("is_banned tg_id={} -> True", tg_id)
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
        owners = list(stmt.scalars().all())
        log_tech.debug("get_owners count={}", len(owners))
        return owners

    async def set_last_query_money(self, tg_id: int, when: datetime | None = None) -> User:
        """
        Метод для установки кулдауна запроса денег
        """
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            raise UserNotFound(tg_id)

        user.last_query_money = when or datetime.now(timezone.utc)

        await self._session.flush()
        log_fin.info("cooldown set tg_id={} when={}", tg_id, user.last_query_money)
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

        log_tech.debug("cd_left tg_id={} left={}", user.tg_id, left)
        return left

    async def check_money(self, user: User, needed: int) -> bool:
        """
        Метод для получения информации, хватает ли у пользователя средств
        """
        ok = user.balance >= needed
        log_tech.debug("check_money tg_id={} needed={} balance={} ok={}", user.tg_id, needed, user.balance, ok)
        return ok

    async def set_rest(self, tg_id: int, until: date) -> User:
        """
        Метод установки реста пользователю
        """
        user = await self.get_by_tg_id(tg_id)

        if user is None:
            raise UserNotFound(tg_id)

        user.rest_until = until
        await self._session.flush()
        log_fin.info("rest set tg_id={} until={}", tg_id, until)
        return user

    async def add_inventory(self, tg_id: int, good_id: str, qty: int = 1) -> User:
        user = await self.get_by_tg_id(tg_id)
        if user is None:
            raise UserNotFound(tg_id)
        inv = dict(user.inventory or {})
        key = str(good_id)
        inv[key] = int(inv.get(key, 0)) + qty
        user.inventory = inv
        await self._session.flush()
        log_fin.info("inventory add tg_id={} good={} qty={} total={}", tg_id, key, qty, inv[key])
        return user

    async def get_active_rests(self) -> list[User]:
        """
        Метод получения пользователей с активным рестом
        """
        today = datetime.now(timezone.utc).date()
        stmt = await self._session.execute(select(User).where(User.rest_until.is_not(None)))
        rows = list(stmt.scalars().all())
        active: list[User] = []
        expired = 0
        for u in rows:
            if u.rest_until is None:
                continue
            if u.rest_until < today:
                log_tech.debug("rest expired tg_id={} until={}", u.tg_id, u.rest_until)
                u.rest_until = None
                expired += 1
            else:
                active.append(u)
        await self._session.flush()
        active.sort(key=lambda u: u.rest_until or today)
        log_tech.info("get_active_rests expired_cleared={} active={}", expired, len(active))
        return active
