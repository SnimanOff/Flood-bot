import sys
from pathlib import Path

from loguru import logger

from src.service.settings import settings

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"

FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.remove()

logger.add(
    sys.stderr,
    level=settings.log_level,
    format=FORMAT,
    colorize=True,
)

logger.add(
    LOG_DIR / "debug.log",
    level="DEBUG",
    filter=lambda record: record["level"].name == "DEBUG",
    format=FORMAT,
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
    colorize=False,
)

logger.add(
    LOG_DIR / "info.log",
    level="INFO",
    filter=lambda record: record["level"].name == "INFO",
    format=FORMAT,
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
    colorize=False,
)

logger.add(
    LOG_DIR / "error.log",
    level="ERROR",
    filter=lambda record: record["level"].name in ("ERROR", "CRITICAL"),
    format=FORMAT,
    rotation="10 MB",
    retention="14 days",
    encoding="utf-8",
    colorize=False,
    backtrace=True,
    diagnose=True,
)

__all__ = ("logger")
