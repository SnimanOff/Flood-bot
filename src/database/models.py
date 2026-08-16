from sqlalchemy import BigInteger, Enum, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from service.vault.roles import Role


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    role: Mapped[Role] = mapped_column(Enum(Role, values_callable=lambda intenum: [enum.value for enum in intenum]), nullable=False, default=Role.USER, server_default=str(Role.USER.value))
