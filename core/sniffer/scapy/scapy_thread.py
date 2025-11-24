__doc__ = "Scapy工具类"
__author__ = "Li Qingyun"
__date__ = "2025-02-27"

import platform

from scapy.all import *

from core.util.io.log_util import LogUtil
from core.util.multithreading.better_thread import BetterThread
from core.util.network.network_interface_util import NetworkInterfaceUtil


class ScapyThread(BetterThread):

    def __init__(self,
                 task_name,
                 output_file_path,
                 network_interface=None,
                 filter_expr=None
                 ):
        """

        :param output_file_path: 输出文件名命名
        :param network_interface: 网卡名称
        :param filter_expr:
        """
        super().__init__()
        # 任务名称
        self.task_name = task_name
        # 输出文件目录
        self.output_file = output_file_path
        # 过滤表达式
        if filter_expr is not None:
            self.filter_expr = filter_expr
        else:
            self.filter_expr = ''
        # 网卡
        self.network_interface = self._detect_interface(network_interface)

        # 抓包结果
        self.packets = None     # 抓取的包列表


    def _detect_interface(self,network_interface):
        """自动检测网络接口"""
        # 如果传入了指定网卡, 就用指定的
        if network_interface is not None and network_interface != 'none':
            return network_interface

        # 如果没指定,先尝试用网卡util获取一下活跃的物理网卡
        active_physical_interface = NetworkInterfaceUtil().get_active_physical_interface()
        if active_physical_interface is not None:
            return NetworkInterfaceUtil().get_active_physical_interface()

        # 如果还是没获取到, 就抛个异常
        raise ValueError('[ScapyThread] 没有可用网卡, 请手动指定网卡名称')


    def run(self):
        """
        重写 Thread 的 run 方法
        :return:
        """
        try:
            LogUtil().debug(self.task_name, '[ScapyProcess] 抓包程序正在启动')
            self._capture()
            LogUtil().debug(self.task_name, '[ScapyProcess] 抓包程序已结束')
        except PermissionError:
            LogUtil().error(self.task_name, "需要root权限执行抓包，请使用sudo运行脚本")
            exit(1)


    def _capture(self):
        """
        抓取流量的核心方法
        :return:
        """
        LogUtil().debug(self.task_name, f'[ScapyProcess] 开启 sniff')
        LogUtil().debug(self.task_name, f'[ScapyProcess] 网卡: {self.network_interface}')
        LogUtil().debug(self.task_name, f'[ScapyProcess] pcap文件: {self.output_file}')

        # 使用sniff抓包，并设置stop_filter以便及时检查stop_event
        try:
            sniff(
                filter=self.filter_expr,
                iface=self.network_interface,
                prn=lambda pkt: wrpcap(self.output_file, pkt, append=True),
                stop_filter=lambda pkt: self.stop_event.is_set()
            )
        except Exception as e:
            LogUtil().error(self.task_name, f'[ScapyProcess] 抓包出现异常: {e}')
        finally:
            LogUtil().debug(self.task_name, f'[ScapyProcess] sniff 结束')


    def clear(self):
        """清理进程"""
        pass


    def stop(self):
        """停止抓包进程"""
        super().stop()


    def get_pcap_path(self):
        return self.output_file


    @staticmethod
    def create_scapy_thread_by_config(task_name, config: dict):

        # 如果没传入配置, 抛异常
        if config is None:
            raise ValueError('[create_scapy_thread_by_config] task_config 参数不能为空')

        # 如果没传入保存路径, 抛异常
        if config.get('output_file_path') is None:
            raise ValueError('[create_scapy_thread_by_config] config中output_file_path 不能为空')
        output_file_path = config.get('output_file_path')

        return ScapyThread(
            task_name=task_name,
            output_file_path=output_file_path,
            network_interface=config.get('network_interface'),
            filter_expr=config.get('filter_expr')
        )
