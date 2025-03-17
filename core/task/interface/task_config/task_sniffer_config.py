__doc__="流量嗅探配置"
__author__="Li Qingyun"
__date__="2025-03-14"

from abc import abstractmethod


class TaskSnifferConfig:
    def __init__(self,
                 scapy_config_dict: dict,
                 connection_tracker_config_dict: dict
                 ):
        """

        :param scapy_config_dict:               Scapy配置
        :param connection_tracker_config_dict:  连接追踪器配置
        """
        self.scapy_config_dict = scapy_config_dict
        self.connection_tracker_config_dict = connection_tracker_config_dict
        pass

    @staticmethod
    @abstractmethod
    def from_dict(origin_sniffer_config_dict: dict):
        """
        从字典创建对象
        :param origin_sniffer_config_dict:
        :return: TaskSnifferConfig 对象
        """
        # 1. Scapy配置
        scapy_config_dict = None
        # 2. 连接追踪器配置
        connection_tracker_config_dict = None

        if origin_sniffer_config_dict.get('scapy_config'):
            scapy_config_dict = origin_sniffer_config_dict.get('scapy_config')

        if origin_sniffer_config_dict.get('connection_tracker_config'):
            connection_tracker_config_dict = origin_sniffer_config_dict.get('connection_tracker_config')

        return TaskSnifferConfig(
            scapy_config_dict=scapy_config_dict,
            connection_tracker_config_dict=connection_tracker_config_dict
        )



    @abstractmethod
    def to_dict(self) -> dict:
        """
        转字典
        :return:
        """
        _result = {}

        if len(self.scapy_config_dict.keys()) > 0:
            _result.update({'scapy_config': self.scapy_config_dict})

        if len(self.connection_tracker_config_dict.keys()) > 0:
            _result.update({'connection_tracker_config': self.connection_tracker_config_dict})

        return _result
        pass