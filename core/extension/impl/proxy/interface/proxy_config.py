__doc__ = "代理配置类"
__author__ = "Li Qingyun"
__date__ = "2025-02-28"

from abc import abstractmethod, ABCMeta


class ProxyConfig(metaclass=ABCMeta):
    """
    代理配置类 (纯虚类, 不可实例化)
    """

    def __init__(self,
                 basic_config_dir: str = None,
                 work_dir: str = None,
                 node_config_dir: str=None,
                 config_file_path: str = None,
                 ):
        """
        初始化
        :param basic_config_dir: 基础配置所在目录
        :param work_dir:         工作目录
        :param node_config_dir:  节点配置所在目录
        :param config_file_path: 配置文件路径
        """
        self.basic_config_dir = basic_config_dir
        self.work_dir = work_dir
        self.node_config_dir = node_config_dir
        self.config_file_path = config_file_path



    @abstractmethod
    def get_binary_file_path(self) -> str:
        """二进制文件路径"""
        pass


    @abstractmethod
    def get_basic_config_dir(self) -> str:
        """代理配置所在目录"""
        pass

    @abstractmethod
    def get_node_config_dir(self) -> str:
        """代理配置所在目录"""
        pass


    @abstractmethod
    def _get_config_file_name(self, protocol_stack) -> str:
        """生成代理的配置文件名"""
        pass


    @abstractmethod
    def get_node_config_file_path(self, protocol_stack) -> str:
        """生成代理配置文件的路径"""


    @abstractmethod
    def get_work_dir(self) -> str:
        """工作目录"""
        pass

    @staticmethod
    @abstractmethod
    def from_dict(config_dict) -> 'ProxyConfig':
        """从字典中生成配置"""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """转换为字典"""
        pass
