__doc__="任务线程类"
__author__="Li Qingyun"
__date__="2025-03-09"

from abc import ABCMeta, abstractmethod

from core.task.interface.config.task_capture_context import TaskCaptureContext, TaskStatus
from core.util.multithreading.better_thread import BetterThread


class TaskThread(BetterThread, metaclass=ABCMeta):
    def __init__(self,
                 task_config_file_path: str=None,
                 name: str=None,
                 ):
        super().__init__(name=f"Task - {name}")
        self.task_config_file_path = task_config_file_path
        self.task_config = None
        pass


    @abstractmethod
    def initial_task_from_config_file(self):
        pass

    @abstractmethod
    def perform_task(self):
        pass

    @abstractmethod
    def task_being_interrupted(self):
        pass

    @abstractmethod
    def finalize(self):
        pass


    def is_finished(self):
        """
        任务是否完成
        :return:
        """
        return self.task_config.capture_context.status == TaskStatus.FINISHED


    @abstractmethod
    def recover_from_context(self):
        """
        恢复上下文
        :return:
        """
        pass

    @abstractmethod
    def continue_perform(self):
        """
        继续执行任务
        :return:
        """
        pass


    @abstractmethod
    def save_config_to_disk(self):
        pass


    @staticmethod
    def create_task_thread_from_config_file(config_file_path: str):
        """
        根据配置创建任务线程
        :param config_file_path:
        :return:
        """
        pass