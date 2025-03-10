# 用途,作者和日期
__doc__ = "扩展类型"
__author__ = "Li Qingyun"
__date__ = "2025-03-09"

import enum


class ExtensionType(enum.Enum):

    """
    扩展类型
    """
    PROXY = 'proxy'
    TOR = 'tor'
    OTHER = 'other'
    UNKNOWN = 'unknown'

    def __str__(self):
        return self.value