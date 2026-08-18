from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.service.logger import log_tech
from src.service.settings import settings

engine = create_async_engine(settings.database, echo=False, pool_pre_ping=True)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def init_db() -> None:
    root = Path(__file__).resolve().parents[2]
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", settings.database)
    log_tech.info("migrations start")
    command.upgrade(cfg, "head")
    log_tech.info("migrations done")


async def close_db() -> None:
    await engine.dispose()
    log_tech.info("engine disposed")
