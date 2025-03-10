__doc__="网页任务线程"
__author__="Li Qingyun"
__date__="2025-03-10"

from abc import ABCMeta, abstractmethod

from core.task.interface.task_thread import TaskThread


class WebsiteTaskThread(TaskThread, metaclass=ABCMeta):

    def __init__(self):
        super().__init__()
        pass

    # def run(self):
    #     self.perform_task()
    #     pass
    #
    # def stop(self):
    #     self.task_being_interrupted()
    #     self.clear()

    @abstractmethod
    def perform_task(self):
        pass

    @abstractmethod
    def task_being_interrupted(self):
        pass

    @abstractmethod
    def clear(self):
        pass
