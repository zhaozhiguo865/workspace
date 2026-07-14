"""
平台模块
"""

from .base import BasePlatform
from .weibo import WeiboPlatform
from .twitter import TwitterPlatform
from .bilibili import BilibiliPlatform
from .zhihu import ZhihuPlatform
from .wechat_mp import WechatMPPlatform
from .xiaohongshu import XiaohongshuPlatform

__all__ = [
    "BasePlatform",
    "WeiboPlatform", 
    "TwitterPlatform",
    "BilibiliPlatform",
    "ZhihuPlatform",
    "WechatMPPlatform",
    "XiaohongshuPlatform"
]