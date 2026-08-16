from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Integer, String, Text
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

    role: Mapped[Role] = mapped_column(Enum(Role, values_callable=lambda intenum: [str(enum.value) for enum in intenum]), nullable=False, default=Role.USER, server_default=str(Role.USER.value))
    banned_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    last_query_money: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class MoneyRequest(Base):
    __tablename__ = "money_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    photo_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True, default=None)
    notifies: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
