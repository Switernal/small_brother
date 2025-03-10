__doc__ = "网站任务偏好"
__author__='Li Qingyun'
__date__='2025-03-10'

from abc import abstractmethod

from core.task.interface.config.task_preference import TaskPreference


class WebsiteTaskPreference(TaskPreference):
    def __init__(self,
                 save_log: bool=True,
                 save_screenshot: bool=True
                 ):
        super().__init__(save_log=save_log)
        self.save_screenshot = save_screenshot
        pass

    @staticmethod
    def from_dict(config_dict):
        """解析capture_preference字典"""
        # 1. 获取save_log字段
        save_log = config_dict.get('save_log', True)

        # 2. 获取save_screenshot字段
        save_screenshot = config_dict.get('save_screenshot', True)

        return WebsiteTaskPreference(save_log=save_log,
                                     save_screenshot=save_screenshot)

    def to_dict(self):
        """转字典"""
        return {
            'save_log': self.save_log,
            'save_screenshot': self.save_screenshot
        }


    @staticmethod
    def comments_for_yaml_data():
        """
        为yaml生成的注释
        :return:
        """
        return {
            'main_comment': '任务偏好',
            'save_log': '是否保存日志',
            'save_screenshot': '是否保存截图'
        }