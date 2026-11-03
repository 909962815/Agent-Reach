# 中文注释：子进程辅助：统一跨平台的文本编码处理。
"""Subprocess helpers for consistent cross-platform text handling."""

from __future__ import annotations

import os
from collections.abc import Mapping

UTF8_ENV = {
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
}


# 返回强制 Python 子进程使用 UTF-8 模式的环境变量。
def utf8_subprocess_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return an environment that forces Python child processes into UTF-8 mode."""
    env = dict(base or os.environ)
    env.update(UTF8_ENV)
    return env
