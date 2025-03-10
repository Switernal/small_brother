__doc__='任务-偏好设置'
__author__='Li Qingyun'
__date__='2025-02-28'

from abc import abstractmethod


class TaskPreference:
    def __init__(self,
                 save_log: bool=True):
        # 偏好设置词典
        self.save_log = save_log        # 是否保存日志
        pass

    @staticmethod
    @abstractmethod
    def from_dict(config_dict):
        """解析capture_preference字典"""
        # 1. 获取save_log字段
        save_log = config_dict.get('save_log', True)
        return TaskPreference(save_log=save_log)

    @abstractmethod
    def to_dict(self):
        """转字典"""
        return {
            'save_log': self.save_log
        }
        pass

    @staticmethod
    @abstractmethod
    def comments_for_yaml_data():
        pass