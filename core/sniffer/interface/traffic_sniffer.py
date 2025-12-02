__doc__ = "流量嗅探器接口"
__author__ = "Li Qingyun"
__date__ = "2025-12-03"

import platform
from abc import ABCMeta, abstractmethod

from core.sniffer.impl.dumpcap.dumpcap_sniffer import DumpcapSniffer
from core.sniffer.impl.scapy.scapy_sniffer import ScapySniffer
from core.sniffer.impl.tcpdump.tcpdump_sniffer import TcpdumpSniffer
from core.util.network.network_interface_util import NetworkInterfaceUtil


class TrafficSniffer(metaclass=ABCMeta):
    def __init__(self,
                 task_name,
                 output_file_path: str,
                 network_interface: str=None,
                 params: dict=None):
        """
        :param output_file_path: 输出文件名命名
        :param network_interface: 网卡名称
        :param params: 指令参数列表
        """
        # 1. 基本属性
        # 1.1 任务名称
        self.task_name = task_name
        # 1.2 输出文件目录
        self.output_file = output_file_path
        # 1.3 指令参数列表
        if params is not None:
            self.params = params
        else:
            self.params = {}
        # 1.4 网卡
        self.network_interface = TrafficSniffer._detect_interface(network_interface)

        # 2. 附加属性
        # 2.1 过滤表达式
        self.filter_expr = None
        # 2.2 启动指令
        self.startup_instruction = None


    @staticmethod
    def _detect_interface(network_interface):
        """
        自动检测网络接口
        """
        # 如果传入了指定网卡, 就用指定的
        if network_interface is not None and network_interface != 'none':
            return network_interface

        # 如果没指定,先尝试用网卡util获取一下活跃的物理网卡
        active_physical_interface = NetworkInterfaceUtil().get_active_physical_interface()
        if active_physical_interface is not None:
            return NetworkInterfaceUtil().get_active_physical_interface()

        # 如果还是没获取到, 就抛个异常
        raise ValueError('[TrafficSniffer] 没有可用网卡, 请手动指定网卡名称')


    @abstractmethod
    def start_sniffer(self):
        """
        启动抓包
        """
        pass


    @abstractmethod
    def stop_sniffer(self):
        """
        停止抓包
        """
        pass

    @abstractmethod
    def generate_filter_expr_by_params(self):
        """
        使用参数列表生成过滤表达式
        """
        pass

    @abstractmethod
    def generate_startup_instruction(self):
        """
        生成启动指令
        """
        pass

    def get_pcap_path(self):
        """
        获取抓包文件路径
        """
        return self.output_file


    @staticmethod
    @abstractmethod
    def creat_sniffer_by_config(task_name, config: dict):
        """
        根据配置创建抓包器实例
        :param task_name: 任务名称
        :param config: 配置字典
        :return: 抓包器实例
        """
        # Windows下用 dumpcap, 其他linux/macOS平台用 tcpdump
        if platform.system() == 'Windows':
            return DumpcapSniffer.creat_sniffer_by_config(task_name, config)
        elif platform.system() == 'Darwin' or platform.system() == 'Linux':
            return TcpdumpSniffer.creat_sniffer_by_config(task_name, config)
        else:
            # raise EnvironmentError(f'[TrafficSniffer] 不支持的操作系统: {platform.system()}')
            # 用 scapy 兜底
            return ScapySniffer.creat_sniffer_by_config(task_name, config)
        pass