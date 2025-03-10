# 用途,作者和日期
__doc__ = "代理软件类型"
__author__ = "Li Qingyun"
__date__ = "2025-02-24"

import enum


class ProxyType(enum.Enum):
    """
    代理类型
    """
    MIHOMO = 'mihomo'
    V2RAY = 'v2ray'
    XRAY = 'xray'
