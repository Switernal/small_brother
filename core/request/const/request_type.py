__doc__="请求类型"
__author__="Li Qingyun"
__date__="2025-03-09"

import enum


class RequestType(enum.Enum):

    """
    请求类型
    """
    BROWSER_CHROME_SINGLE_TAB = 'browser_chrome_single_tab'
    BROWSER_CHROME_MULTI_TAB = 'browser_chrome_multi_tab'
    # BROWSER_FIREFOX = 'browser_firefox'
    # APPLICATION = 'application'
    # DNS = 'dns'
    # DOH = 'DNS over HTTPS'
    # DOQ = 'DNS over QUIC'


    def __str__(self):
        return self.value