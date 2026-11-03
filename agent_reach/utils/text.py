# 中文注释：文本辅助：脱敏 URL 里的凭据等敏感信息。
"""Text helpers."""

from __future__ import annotations

import re

_URL_CREDENTIALS_RE = re.compile(
    r"([A-Za-z][A-Za-z0-9+.\-]{0,19}://)[^/\s@]+@"
)
_BARE_USERINFO_RE = re.compile(
    r"(?<![A-Za-z0-9._%+\-])[^:/\s@]+:[^/\s@]+@(?=[A-Za-z0-9.\-\[])"
)
_URL_QUERY_SECRET_RE = re.compile(
    r"([?&#](?:"
    r"access[_-]?token|auth[_-]?token|token|bearer|"
    r"api[_-]?key|key|password|passwd|secret|"
    r"signature|sig|session(?:id)?|cookie|credential"
    r")=)[^&#\s]*",
    re.IGNORECASE,
)


# 脱敏文本里 URL 的用户信息和敏感查询参数或片段值。
def scrub_url_credentials(text: object) -> str:
    """Redact URL userinfo and sensitive query/fragment values from text."""
    scrubbed = _URL_CREDENTIALS_RE.sub(r"\1***@", str(text))
    scrubbed = _BARE_USERINFO_RE.sub("***@", scrubbed)
    return _URL_QUERY_SECRET_RE.sub(r"\1***", scrubbed)
