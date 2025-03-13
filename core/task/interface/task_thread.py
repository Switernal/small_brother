__doc__="任务线程类"
__author__="Li Qingyun"
__date__="2025-03-09"

from abc import ABCMeta, abstractmethod

from core.task.const.task_type import TaskType
from core.task.interface.task_config import TaskConfig
from core.task.interface.task_config.task_capture_context import TaskCaptureContext, TaskStatus
from core.task.interface.task_progress import TaskProgress
from core.util.io.yaml_util import YamlUtil
from core.util.multithreading.better_thread import BetterThread


class TaskThread(BetterThread, metaclass=ABCMeta):
    def __init__(self,
                 task_name: str = None,
                 task_config_file_path: str=None,
                 task_config: TaskConfig = None
                 ):
        super().__init__(name=f"TaskThread-{task_name}")

        self.task_name = task_name

        # 任务配置
        self.task_config_file_path = task_config_file_path
        self.task_config = task_config

        # 任务进度(当前进度, 总进度)
        self.task_progress = TaskProgress(current_progress=0, total_progress=0)
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
        config = YamlUtil().load(config_file_path)

        if config.get('task_type'):
            task_type = TaskType(config.get('task_type'))
        else:
            raise ValueError(f"[TaskThread] 任务配置文件 {config_file_path} 中没有指定任务类型")

        # 判断任务类型, 返回对应的线程
        if task_type == TaskType.WEBSITE_SINGLE_TAB:
            from core.task.impl.website.single_tab.website_single_tab_task_thread import WebsiteSingleTabTaskThread
            return WebsiteSingleTabTaskThread.create_task_from_config_file(task_config_file_path=config_file_path)
        pass