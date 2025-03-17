__doc__ = "代理软件类型"
__author__ = "Li Qingyun"
__date__ = "2025-02-24"

import enum


class ProxyType(enum.Enum):
    """
    代理类型
    """
    MIHOMO = 'mihomo'   # mihomo内核
    V2RAY = 'v2ray'     # v2ray内核
    XRAY = 'xray'       # xray内核

    def __str__(self):
        return self.value
