__doc__ = "scapy 嗅探器"
__author__ = "Li Qingyun"
__date__ = "2025-12-03"

from core.sniffer.impl.scapy.scapy_thread import ScapyThread
from core.sniffer.interface.traffic_sniffer import TrafficSniffer


class ScapySniffer(TrafficSniffer):
    """
    scapy 嗅探器
    """

    def generate_filter_expr_by_params(self):
        pass

    def generate_startup_instruction(self):
        pass

    def __init__(self,
                 task_name: str,
                 output_file_path: str,
                 network_interface: str = None,
                 params: dict = None
                 ):
        """

        :param task_name:           任务名称
        :param output_file_path:    输出文件路径
        :param network_interface:   网络接口
        :param params:              指令参数列表
        """

        # 1. 初始化父类
        self.task_name = task_name
        self.output_file_path = output_file_path
        self.network_interface = network_interface
        self.params = params

        super().__init__(
            task_name=task_name,
            output_file_path=output_file_path,
            network_interface=network_interface,
            params=params
        )


        # 2. 创建scapy线程
        self.scapy_thread = ScapyThread.create_scapy_thread_by_config(task_name=self.task_name,
                                                                      config={
                                                                                'output_file_path': self.output_file,
                                                                                'network_interface': self.network_interface,
                                                                                'filter_expr': self.filter_expr,
                                                                             })
        pass


    def start_sniffer(self):
        """
        启动抓包
        """
        self.scapy_thread.start()
        pass

    def stop_sniffer(self):
        """
        停止抓包
        """
        if self.scapy_thread is not None:
            self.scapy_thread.stop()
        pass

    @staticmethod
    def creat_sniffer_by_config(task_name, config: dict):
        return ScapySniffer(
            task_name=task_name,
            output_file_path=config.get('output_file_path'),
            network_interface=config.get('network_interface'),
            params=config.get('params'),
        )
        pass

    def handle_log(self):
        pass