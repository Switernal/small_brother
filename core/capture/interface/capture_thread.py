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
                 task_name: str,
                 capture_name: str,
                 timeout: int,
                 extension_config,
                 request_config,
                 sniffer_config,
                 sniffer_conn_tracker_config
                 ):
        """
        构造函数
        :param task_name:                       隶属于的任务名
        :param capture_name:                    Capture进程名称
        :param timeout:                         抓取超时时间(秒)
        :param extension_config:                Extension子线程配置
        :param request_config:                  Request子线程配置
        :param sniffer_config:                  流量抓包器子线程配置
        :param sniffer_conn_tracker_config:     ConnectionTracker线程配置
        """
        super().__init__(name=f"CaptureThread-{capture_name}")

        # 进程信息
        self.task_name = task_name
        self.capture_name = capture_name

        # 抓取超时时间
        self.timeout = timeout

        # 配置字典
        self.extension_config = extension_config
        self.request_config = request_config
        self.sniffer_config = sniffer_config
        self.sniffer_conn_tracker_config = sniffer_conn_tracker_config


    @abstractmethod
    def _start_capture(self):
        """
        启动抓取流程
        :return:
        """
        pass