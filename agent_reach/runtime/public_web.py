# 中文注释：公开优先查询：复用 Web 频道，不用浏览器、不做站点抓取规则。
"""Public-first queries reuse WebChannel; no browser or site extraction rules."""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from agent_reach.channels.base import Action, Channel
from agent_reach.utils.url import host_matches, normalize_public_http_url

from .result import UPSTREAM_BROKEN

BACKEND = "public-web"
MAX_SECONDS = 20.0


# 内部：判断输入是否在公开查询范围内。
def _in_scope(url: str, scopes: tuple[str, ...]) -> bool:
    try:
        url = normalize_public_http_url(url)
        path = urlsplit(url).path
    except ValueError:
        return False
    for scope in scopes:
        host, _, prefix = scope.partition("/")
        if host_matches(url, host) and (not prefix or path.startswith("/" + prefix)):
            return True
    return False


# 内部：拒绝空壳页面和明显的登录或验证页面，不拦正文里的登录链接。
def _readable(item: dict) -> bool:
    """Reject empty shells and clear login/challenge pages, not inline login links.

    ponytail: this is a conservative text check, not proof of a complete article.
    The response always says page_text with completeness unverified.
    """
    text = str(item.get("text") or "").strip()
    title = str(item.get("title") or "").strip()
    if not text or (len(text) < 80 and text.casefold() == title.casefold()):
        return False
    wall = r"log\s*in|sign\s*in|join\s+(?:now|linkedin)|登录|登入|注册|just a moment|prove your humanity|access denied|security verification|安全验证|验证码"
    if re.fullmatch(rf"(?:{wall})(?:\s*[-|·:].*)?", title, re.I):
        return False
    login_only = (r"(?:(?:please\s+)?(?:log\s*in|sign\s*in)(?:\s+to\s+continue)?[.!?\s]*|"
                  r"(?:请)?(?:登录|登入)(?:后继续|以继续)?[。！\s]*)+")
    return re.fullmatch(login_only, text, re.I) is None


# 返回一次有范围的 Web 查询结果；输入没有公开路线时返回 None。
def attempt(channel: Channel, action: Action, params: dict, *, timeout: float) -> dict | None:
    """Return a scoped Web result, or None when this input has no public route."""
    if not action.public_web:
        return None
    from agent_reach.channels.web import WebChannel

    from .dispatch import run_action

    if action.name in {"search", "jobs"}:
        query = " ".join(str(params[k]) for k in ("query", "location", "city") if params.get(k))
        scope = " OR ".join("site:" + url for url in action.public_web)
        web_action = "search"
        web_params = {"query": f"({query}) ({scope})", "limit": params.get("limit", 5)}
    elif action.name == "read" and _in_scope(str(params.get("target", "")), action.public_web):
        web_action = "read"
        web_params = {"target": params["target"]}
    else:
        return None

    out = run_action(WebChannel(), web_action, web_params, timeout=timeout)
    out["channel"], out["action"] = channel.name, action.name
    if out["ok"]:
        items = [item for item in out["items"] if _in_scope(str(item.get("url") or ""), action.public_web)]
        if web_action == "read":
            items = [item for item in items if _readable(item)]
        if not items:
            out.update(ok=False, backend=None, items=[], error={"code": UPSTREAM_BROKEN,
                       "message": "Public web returned no usable content in the requested scope",
                       "hint": "Try the site tool; this does not establish a login requirement."})
            out["meta"]["attempts"].append({"backend": "content-check", "result": "INSUFFICIENT_CONTENT"})
        else:
            scope = "search_results" if web_action == "search" else "page_text"
            for item in items:
                item["raw"] = {"source": item.get("raw"), "content_scope": scope,
                               "access": "public", "completeness_verified": False}
            out.update(backend=BACKEND, items=items)
            out["meta"]["access"] = {"mode": "public", "scope": scope, "completeness_verified": False,
                "note": "公开网页结果；不保证站内排序、最新状态、全文或全部评论。需要站内数据时指定 --backend。"}
    # Provider 429/errors belong to Web, never to the destination platform.
    out["meta"]["attempts"] = [{**row, "backend": BACKEND + "/" + row["backend"]}
                                for row in out["meta"]["attempts"]]
    return out
