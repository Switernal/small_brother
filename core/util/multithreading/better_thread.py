__doc__='更好的进程类'
__author__='Li Qingyun'
__date__='2025-03-07'

import threading
from abc import ABCMeta, abstractmethod


class BetterThread(threading.Thread, metaclass=ABCMeta):
    """
    对 threading.Thread 包装, 提供停止方法和清理方法
    """

    def __init__(self, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(target, target=target, name=name,
                         args=args, kwargs=kwargs, daemon=daemon)

        # 停止事件
        self.stop_event = threading.Event()


    @abstractmethod
    def clear(self):
        """
        清理资源
        :return:
        """
        pass


    def stop(self):
        """
        停止线程
        :return:
        """
        self.stop_event.set()
        pass