"""Version info from GitHub releases/tags (fetched once at startup)."""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Any

import aiohttp

from src.service.logger import log_tech
from src.service.settings import settings

FALLBACK_VERSION = "0.0.0"

_lock = asyncio.Lock()

_cache: dict[str, Any] = {
    "version": FALLBACK_VERSION,
    "updated_at": None,
    "fetched_at": None,
}


def format_ago(when: datetime | None) -> str:
    if when is None:
        return "неизвестно"
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    secs = int((now - when.astimezone(timezone.utc)).total_seconds())
    if secs < 0:
        secs = 0
    if secs < 60:
        return "только что"
    if secs < 3600:
        return f"{secs // 60} мин. назад"
    if secs < 86400:
        return f"{secs // 3600} ч. назад"
    if secs < 86400 * 30:
        return f"{secs // 86400} дн. назад"
    return when.astimezone(timezone.utc).strftime("%d.%m.%Y")


def _headers() -> dict[str, str]:
    h = {"Accept": "application/vnd.github+json", "User-Agent": "flood-currency-bot"}
    if settings.github_token:
        h["Authorization"] = f"Bearer {settings.github_token}"
    return h


def _strip_v(tag: str) -> str:
    t = (tag or "").strip()
    if t.lower().startswith("v") and len(t) > 1 and t[1].isdigit():
        return t[1:]
    return t or FALLBACK_VERSION


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


async def _fetch_github() -> tuple[str, datetime | None] | None:
    """Return (version, when) from releases → tags → commits date only."""
    repo = (settings.github_repo or "").strip()
    if not repo or "/" not in repo:
        return None
    base = f"https://api.github.com/repos/{repo}"
    timeout = aiohttp.ClientTimeout(total=8)
    async with aiohttp.ClientSession(timeout=timeout, headers=_headers()) as session:
        async with session.get(f"{base}/releases/latest") as resp:
            if resp.status == 200:
                data = await resp.json()
                tag = data.get("tag_name") or ""
                when = _parse_dt(data.get("published_at") or data.get("created_at"))
                if tag:
                    return _strip_v(tag), when

        async with session.get(f"{base}/tags", params={"per_page": 1}) as resp:
            if resp.status == 200:
                tags = await resp.json()
                if isinstance(tags, list) and tags:
                    tag = tags[0].get("name") or ""
                    when: datetime | None = None
                    sha = (tags[0].get("commit") or {}).get("sha")
                    if sha:
                        async with session.get(f"{base}/commits/{sha}") as cresp:
                            if cresp.status == 200:
                                cdata = await cresp.json()
                                when = _parse_dt(
                                    (cdata.get("commit") or {})
                                    .get("committer", {})
                                    .get("date")
                                )
                    if tag:
                        return _strip_v(tag), when

        branch = settings.github_branch or "main"
        async with session.get(f"{base}/commits/{branch}") as resp:
            if resp.status != 200:
                log_tech.warning("github commits status={}", resp.status)
                return None
            data = await resp.json()
            when = _parse_dt(
                (data.get("commit") or {}).get("committer", {}).get("date")
            )
            return FALLBACK_VERSION, when


async def refresh_version() -> None:
    async with _lock:
        try:
            result = await _fetch_github()
            if result is not None:
                ver, when = result
                _cache["version"] = ver or FALLBACK_VERSION
                if when is not None:
                    _cache["updated_at"] = when
                log_tech.info(
                    "version refreshed version={} updated_at={}",
                    _cache["version"],
                    _cache["updated_at"],
                )
            else:
                log_tech.warning("version github unavailable")
        except Exception:
            log_tech.exception("version refresh failed")
        if _cache["updated_at"] is None:
            _cache["updated_at"] = datetime.now(timezone.utc)
        _cache["fetched_at"] = datetime.now(timezone.utc)


def get_version_info() -> tuple[str, str]:
    return str(_cache["version"]), format_ago(_cache.get("updated_at"))


def get_cached_version() -> str:
    return str(_cache["version"])


def get_cached_ago() -> str:
    return format_ago(_cache.get("updated_at"))


def get_app_version() -> str:
    return str(_cache["version"])
