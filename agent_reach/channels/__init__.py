# -*- coding: utf-8 -*-
# 中文注释：频道注册表：agent-reach <频道> <动作> 对应的全部平台都在这里登记。
"""
Channel registry — every platform exposed by `agent-reach <channel> <action>`.
"""

from typing import List, Optional

from .base import Channel
from .bilibili import BilibiliChannel
from .boss import BossChannel
from .facebook import FacebookChannel
from .github import GitHubChannel
from .instagram import InstagramChannel
from .linkedin import LinkedInChannel
from .reddit import RedditChannel
from .twitter import TwitterChannel
from .v2ex import V2EXChannel
from .web import WebChannel
from .xiaohongshu import XiaoHongShuChannel
from .xiaoyuzhou import XiaoyuzhouChannel
from .xueqiu import XueqiuChannel
from .youtube import YouTubeChannel

ALL_CHANNELS: List[Channel] = [
    GitHubChannel(),
    TwitterChannel(),
    YouTubeChannel(),
    RedditChannel(),
    FacebookChannel(),
    InstagramChannel(),
    BilibiliChannel(),
    XiaoHongShuChannel(),
    LinkedInChannel(),
    BossChannel(),
    V2EXChannel(),
    XueqiuChannel(),
    XiaoyuzhouChannel(),
    WebChannel(),
]


# 按名字取一个频道。
def get_channel(name: str) -> Optional[Channel]:
    """Get a channel by name."""
    for ch in ALL_CHANNELS:
        if ch.name == name:
            return ch
    return None


# 取全部已注册频道。
def get_all_channels() -> List[Channel]:
    """Get all registered channels."""
    return ALL_CHANNELS


__all__ = [
    "Channel",
    "ALL_CHANNELS",
    "get_channel",
    "get_all_channels",
]
