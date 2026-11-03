# -*- coding: utf-8 -*-
# 中文注释：跨频道后端：一个后端可服务多个频道（例如 OpenCLI 覆盖小红书、Reddit、X、Facebook、Instagram 等）。
"""Cross-channel backends.

A backend here is an upstream runtime that serves MULTIPLE channels
(e.g. OpenCLI covers xiaohongshu/reddit/twitter/facebook/instagram through
the Agent Reach browser).
"""

from .opencli import OPENCLI_EXTENSION_URL, opencli_call, opencli_items  # noqa: F401
