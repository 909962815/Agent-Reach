# 中文注释：版本提醒：仅在显式 update --check 时联网查询，不跑后台进程。
"""Version notices from an explicit update --check only; no background process."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Optional

from agent_reach import __version__
from agent_reach.utils.paths import (
    PrivatePathError,
    atomic_write_private_text,
    make_private_dir,
    read_small_text_no_follow,
)

from . import state

REPO = "Panniantong/Agent-Reach"
FETCH_TIMEOUT = 10.0
NOTES_MAX = 2000


# 返回版本提醒缓存的路径。
def cache_path() -> Path:
    return state.root() / "update-check.json"


# 把版本号解析成可比较的元组。
def version_tuple(v: str) -> tuple:
    try:
        return tuple(int(x) for x in str(v).strip().lstrip("v").split("."))
    except ValueError:
        return ()


# 取最新 GitHub 发布的 {最新版，说明}；网络错误时抛出。
def fetch_latest(timeout: float = FETCH_TIMEOUT) -> dict:
    """{latest, notes} of the latest GitHub release. Raises on network errors."""
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest",
                                 headers={"User-Agent": "agent-reach", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        rel = json.loads(resp.read())
    return {"latest": str(rel.get("tag_name", "")).lstrip("v"), "notes": (rel.get("body") or "")[:NOTES_MAX]}


# 写版本提醒缓存。
def write_cache(info: dict) -> None:
    make_private_dir(state.root())
    state.remember_path(cache_path(), "explicit update check")
    atomic_write_private_text(cache_path(), json.dumps(
        {"checked_at": state.now(), "latest": info["latest"], "notes": info["notes"]}, ensure_ascii=False))


# 读版本提醒缓存。
def read_cache() -> Optional[dict]:
    try:
        data = json.loads(read_small_text_no_follow(cache_path(), max_bytes=64 * 1024) or "null")
    except (OSError, ValueError, PrivatePathError):
        return None
    return data if isinstance(data, dict) else None


# 缓存的最新版比当前版新时，返回 {当前版，最新版，说明}。
def notice() -> Optional[dict]:
    """{current, latest, notes} when the cached latest release is newer than this version."""
    data = read_cache()
    if not data:
        return None
    latest = str(data.get("latest") or "")
    current = version_tuple(__version__)
    if not current or version_tuple(latest) <= current:
        return None
    return {"current": __version__, "latest": latest, "notes": str(data.get("notes") or "")}
