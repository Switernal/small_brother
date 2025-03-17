__doc__="任务配置类"
__author__="Li Qingyun"
__date__="2025-03-10"

from abc import ABCMeta, abstractmethod

from core.task.const.task_type import TaskType
from core.task.interface.task_config.task_capture_context import TaskCaptureContext
from core.task.interface.task_config.task_capture_policy import TaskCapturePolicy
from core.task.interface.task_config.task_extension_config import TaskExtensionConfig
from core.task.interface.task_config.task_preference import TaskPreference
from core.task.interface.task_config.task_request_config import TaskRequestConfig
from core.task.interface.task_config.task_sniffer_config import TaskSnifferConfig


class TaskConfig(metaclass=ABCMeta):
    """
    任务配置的抽象类
        用于解析任务配置文件, 并生成任务配置对象
        不可实例化, 需要继承后实现
    """
    def __init__(self,
                 task_name: str,
                 task_note: str,
                 task_type: TaskType,
                 output_dir: str,
                 extension_config: TaskExtensionConfig,
                 request_config: TaskRequestConfig,
                 sniffer_config: TaskSnifferConfig,
                 capture_policy: TaskCapturePolicy,
                 capture_context: TaskCaptureContext,
                 preference: TaskPreference=None
                 ):
        """
        :param task_name:           任务名称
        :param task_note:           任务备注
        :param task_type:           任务类型
        :param output_dir:          输出目录
        :param extension_config:    扩展配置
        :param request_config:      请求配置
        :param sniffer_config:      流量嗅探配置
        :param capture_policy:      抓取策略
        :param capture_context:     上下文
        :param preference:          偏好
        """
        self.task_name = task_name
        self.task_note = task_note
        self.task_type = task_type
        self.output_dir = output_dir
        self.extension_config = extension_config
        self.request_config = request_config
        self.sniffer_config = sniffer_config
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