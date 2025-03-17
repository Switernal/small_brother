# 用途,作者和日期
__doc__ = "扩展类型"
__author__ = "Li Qingyun"
__date__ = "2025-03-09"

import enum


class ExtensionType(enum.Enum):

    """
    扩展类型
    """
    PROXY = 'proxy'         # 代理
    TOR = 'tor'             # Tor
    OTHER = 'other'         # 其他
    UNKNOWN = 'unknown'     # 未知

    def __str__(self):
        return self.value