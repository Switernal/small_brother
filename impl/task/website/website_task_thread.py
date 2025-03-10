__doc__="网页任务线程"
__author__="Li Qingyun"
__date__="2025-03-10"

from abc import ABCMeta

from core.task.interface.task_thread import TaskThread


class WebsiteTaskThread(TaskThread, metaclass=ABCMeta):

    def __init__(self):
        super().__init__()
        pass

    def run(self):
        self.perform_task()
        pass

    def stop(self):
        self.task_being_interrupted()
        self.clear()

    def perform_task(self):
        pass


    def task_being_interrupted(self):
        pass


    def clear(self):
        pass
