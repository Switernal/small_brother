__doc__="Capture 抓取流量线程"
__author__="Li Qingyun"
__date__="2025-03-07"

from abc import abstractmethod

from core.util.multithreading.better_thread import BetterThread

class CaptureThread(BetterThread):
    """
    Capture 抓取流量线程
    """

    def __init__(self,
                 name: str,
                 extension_config,
                 request_config,
                 sniffer_scapy_config,
                 sniffer_conn_tracker_config
                 ):
        """
        构造函数
        :param name:                            线程名
        :param extension_config:                扩展子线程配置
        :param request_config:                  请求子线程配置
        :param sniffer_scapy_config:            抓包子线程配置
        :param sniffer_conn_tracker_config:     连接追踪子线程配置
        """
        super().__init__(name=f"CaptureThread-{name}")

        self.extension_config = extension_config
        self.request_config = request_config
        self.sniffer_scapy_config = sniffer_scapy_config
        self.sniffer_conn_tracker_config = sniffer_conn_tracker_config


    @abstractmethod
    def _start_capture(self):
        pass