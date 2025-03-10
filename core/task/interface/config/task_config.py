__doc__="任务配置类"
__author__="Li Qingyun"
__date__="2025-03-10"

from abc import ABCMeta, abstractmethod

from core.task.const.task_type import TaskType
from core.task.interface.config.task_capture_context import TaskCaptureContext
from core.task.interface.config.task_capture_policy import TaskCapturePolicy
from core.task.interface.config.task_extension_config import TaskExtensionConfig
from core.task.interface.config.task_preference import TaskPreference
from core.task.interface.config.task_request_config import TaskRequestConfig


class TaskConfig(metaclass=ABCMeta):
    def __init__(self,
                 task_name: str,
                 task_note: str,
                 task_type: TaskType,
                 output_dir: str,
                 extension_config: TaskExtensionConfig,
                 request_config: TaskRequestConfig,
                 capture_policy: TaskCapturePolicy,
                 capture_context: TaskCaptureContext,
                 preference: TaskPreference=None
                 ):
        self.task_name = task_name
        self.task_note = task_note
        self.task_type = task_type
        self.output_dir = output_dir
        self.extension_config = extension_config
        self.request_config = request_config
        self.capture_policy = capture_policy
        self.capture_context = capture_context
        self.preference = preference


    @staticmethod
    @abstractmethod
    def create_task_config_from_file(config_file_path: str):
        """
        根据配置创建任务配置类
        """
        pass


    @abstractmethod
    def convert_to_yaml_data(self) -> dict:
        """
        转成yaml格式数据
        """
        pass


    @abstractmethod
    def convert_to_commented_yaml_data(self):
        """
        从yaml格式数据创建
        """
        pass


    @abstractmethod
    def comments_for_yaml_data(self) -> dict:
        """
        给yaml的注释
        :return:
        """
        pass