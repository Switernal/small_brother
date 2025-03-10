__doc__ = '任务-请求配置'
__author__ = 'Li Qingyun'
__date__ = '2025-03-10'

from abc import ABCMeta, abstractmethod


class TaskRequestConfig(metaclass=ABCMeta):
    def __init__(self,
                 config_dict: dict,
                 ):
        self.config_dict = config_dict
        pass

    @staticmethod
    @abstractmethod
    def from_dict(origin_request_config_dict: dict):
        pass


    @abstractmethod
    def to_dict(self) -> dict:
        pass