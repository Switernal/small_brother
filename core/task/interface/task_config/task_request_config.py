__doc__ = '任务-请求配置'
__author__ = 'Li Qingyun'
__date__ = '2025-03-10'

from abc import ABCMeta, abstractmethod


class TaskRequestConfig(metaclass=ABCMeta):
    """
    任务请求配置
        用于解析任务配置文件中的请求配置, 并生成任务请求配置对象
        不可实例化, 需要继承后实现
    """
    def __init__(self,
                 config_dict: dict,
                 ):
        """

        :param config_dict:
        """
        self.config_dict = config_dict
        pass

    @staticmethod
    @abstractmethod
    def from_dict(origin_request_config_dict: dict):
        pass


    @abstractmethod
    def to_dict(self) -> dict:
        pass