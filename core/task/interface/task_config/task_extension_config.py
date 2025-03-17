__doc__ = '任务-扩展配置'
__author__ = 'Li Qingyun'
__date__ = '2025-03-10'

from abc import ABCMeta, abstractmethod


class TaskExtensionConfig(metaclass=ABCMeta):
    """
    任务扩展(Extension)配置的抽象类
        用于解析任务配置文件中的扩展配置, 并生成任务扩展配置对象
        不可实例化, 需要继承后实现
    """
    def __init__(self,
                 config_dict: dict,
                 ):
        self.config_dict = config_dict
        pass

    @staticmethod
    @abstractmethod
    def from_dict(origin_extension_config_dict: dict):
        pass


    @abstractmethod
    def to_dict(self) -> dict:
        pass