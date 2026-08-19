"""Version info from GitHub releases/tags (TTL cache)."""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Any

import aiohttp
from packaging.version import InvalidVersion, Version

from src.service.logger import log_tech
from src.service.settings import settings

FALLBACK_VERSION = "0.0.0"
CACHE_TTL = 60

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


def _tag_key(name: str):
    s = _strip_v(name)
    try:
        return (0, Version(s))
    except InvalidVersion:
        return (1, s)


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


async def _commit_date(session: aiohttp.ClientSession, base: str, sha: str) -> datetime | None:
    async with session.get(f"{base}/commits/{sha}") as cresp:
        if cresp.status != 200:
            return None
        cdata = await cresp.json()
        return _parse_dt(
            (cdata.get("commit") or {}).get("committer", {}).get("date")
        )


async def _branch_date(session: aiohttp.ClientSession, base: str) -> datetime | None:
    branch = settings.github_branch or "main"
    async with session.get(f"{base}/commits/{branch}") as resp:
        if resp.status != 200:
            log_tech.warning("github commits status={}", resp.status)
            return None
        data = await resp.json()
        return _parse_dt(
            (data.get("commit") or {}).get("committer", {}).get("date")
        )


async def _fetch_github() -> tuple[str, datetime | None] | None:
    """releases/latest → releases list → best tag by semver → branch date fallback."""
    repo = (settings.github_repo or "").strip()
    if not repo or "/" not in repo:
        return None
    base = f"https://api.github.com/repos/{repo}"
    timeout = aiohttp.ClientTimeout(total=8)
    async with aiohttp.ClientSession(timeout=timeout, headers=_headers()) as session:
        # 1. Formal latest release
        async with session.get(f"{base}/releases/latest") as resp:
            if resp.status == 200:
                data = await resp.json()
                tag = data.get("tag_name") or ""
                when = _parse_dt(data.get("published_at") or data.get("created_at"))
                if tag:
                    return _strip_v(tag), when

        # 2. First non-draft release
        async with session.get(f"{base}/releases", params={"per_page": 20}) as resp:
            if resp.status == 200:
                releases = await resp.json()
                if isinstance(releases, list):
                    for rel in releases:
                        if rel.get("draft"):
                            continue
                        tag = rel.get("tag_name") or ""
                        if not tag:
                            continue
                        when = _parse_dt(rel.get("published_at") or rel.get("created_at"))
                        return _strip_v(tag), when

        # 3. Best tag by packaging.version
        version = FALLBACK_VERSION
        when: datetime | None = None
        async with session.get(f"{base}/tags", params={"per_page": 100}) as resp:
            if resp.status == 200:
                tags = await resp.json()
                if isinstance(tags, list) and tags:
                    best = max(tags, key=lambda t: _tag_key(t.get("name") or ""))
                    tag_name = best.get("name") or ""
                    if tag_name:
                        version = _strip_v(tag_name)
                        sha = (best.get("commit") or {}).get("sha")
                        if sha:
                            when = await _commit_date(session, base, sha)

        # 4. commits/{branch} only for updated_at if tag has no date
        if when is None:
            when = await _branch_date(session, base)

        return version, when


async def refresh_version(force: bool = False) -> None:
    async with _lock:
        if not force and _cache["fetched_at"] is not None:
            age = (datetime.now(timezone.utc) - _cache["fetched_at"]).total_seconds()
            if age < CACHE_TTL:
                return
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


async def get_version_info() -> tuple[str, str]:
    await refresh_version(force=False)
    return str(_cache["version"]), format_ago(_cache.get("updated_at"))


def get_cached_version() -> str:
    return str(_cache["version"])


def get_cached_ago() -> str:
    return format_ago(_cache.get("updated_at"))


def get_app_version() -> str:
    return str(_cache["version"])
