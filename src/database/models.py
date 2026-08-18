from datetime import datetime, date, timezone

from sqlalchemy import BigInteger, DateTime, Enum, Integer, JSON, String, Text, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.service.vault.roles import Role


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    inventory: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="{}")

    role: Mapped[Role] = mapped_column(Enum(Role, values_callable=lambda intenum: [str(enum.value) for enum in intenum]), nullable=False, default=Role.USER, server_default=str(Role.USER.value))
    banned_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    last_query_money: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    rest_until: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)

class MoneyRequest(Base):
    __tablename__ = "money_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    photo_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True, default=None)
    notifies: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class Check(Base):
    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    good_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    good_title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
