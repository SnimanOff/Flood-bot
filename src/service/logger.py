import sys
from pathlib import Path

from loguru import logger as _logger

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)

FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<yellow>{extra[channel]}</yellow> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

_logger.remove()
_logger.configure(extra={"channel": "-"})


def _ch(name: str):
    return lambda r: r["extra"].get("channel") == name


def _err(r):
    return r["level"].name in ("ERROR", "CRITICAL")


_logger.add(sys.stderr, level="INFO", format=FORMAT, colorize=True)
_logger.add(
    LOG_DIR / "app.log",
    level="INFO",
    filter=_ch("app"),
    format=FORMAT,
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
    colorize=False,
)
_logger.add(
    LOG_DIR / "tech.log",
    level="DEBUG",
    filter=_ch("tech"),
    format=FORMAT,
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
    colorize=False,
)
_logger.add(
    LOG_DIR / "finance.log",
    level="INFO",
    filter=_ch("finance"),
    format=FORMAT,
    rotation="10 MB",
    retention="14 days",
    encoding="utf-8",
    colorize=False,
)
_logger.add(
    LOG_DIR / "error.log",
    level="ERROR",
    filter=_err,
    format=FORMAT,
    rotation="10 MB",
    retention="14 days",
    encoding="utf-8",
    colorize=False,
    backtrace=True,
    diagnose=True,
)

log_app = _logger.bind(channel="app")
log_tech = _logger.bind(channel="tech")
log_fin = _logger.bind(channel="finance")
logger = log_app

__all__ = ("logger", "log_app", "log_tech", "log_fin")
