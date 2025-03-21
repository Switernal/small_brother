__doc__='任务-上下文'
__author__='Li Qingyun'
__date__='2025-02-28'

from abc import abstractmethod
from core.task.const.task_status import TaskStatus


class TaskCaptureContext:

    def __init__(self,
                 status: TaskStatus,
                 counter: int,
                 last_perform_time,
                 capture_performed_times
                 ):
        """

        :param status:                  任务状态
        :param counter:                 计数器(类似CPU指令计数器, 主要是记录执行位置, 比如第几个网站这样)
        :param last_perform_time:       最后一次执行时间
        :param capture_performed_times: 抓取次数
        """
        self.status = status                                        # 任务状态
        self.counter = counter                                      # 计数器
        self.last_perform_time = last_perform_time                  # 最后一次执行时间
        self.capture_performed_times = capture_performed_times      # 抓取次数
        pass

    def increase_counter(self):
        """
        计数器自增
        :return:
        """
        self.counter += 1
        pass

    def update_counter(self, new_counter):
        """
        更新计数器
        :param new_counter: 新计数值
        :return:
        """
        self.counter = new_counter
        pass

    def update_status(self, new_status: TaskStatus):
        """
        更新任务状态
        :param new_status: TaskStatus 类型
        :return:
        """
        self.status = new_status
        pass

    def update_last_perform_time(self, new_time):
        """
        更新最后一次执行时间
        :param new_time:
        :return:
        """
        self.last_perform_time = new_time
        pass

    def increase_capture_performed_times(self):
        """更新抓取次数"""
        self.capture_performed_times += 1
        pass

    def clear_capture_performed_times(self):
        """清空抓取次数"""
        self.capture_performed_times = 0

    @staticmethod
    @abstractmethod
    def from_dict(config_dict):
        """解析capture_context字典"""
        # 1. 状态
        if config_dict.get('status'):
            status = TaskStatus(config_dict['status'])
        else:
            status = TaskStatus.INITIAL

        # 2. 计数器
        counter = config_dict.get('counter', 0)

        # 3. 最后一次执行时间
        last_perform_time = config_dict.get('last_perform_time', None)

        # 4. 抓取次数
        capture_performed_times = config_dict.get('capture_performed_times', 0)

        return TaskCaptureContext(
            status=status,
            counter=counter,
            last_perform_time=last_perform_time,
            capture_performed_times=capture_performed_times
        )


    @abstractmethod
    def to_dict(self):
        """转字典"""
        return {
            'status': self.status.value,
            'counter': self.counter,
            'last_perform_time': self.last_perform_time,
            'capture_performed_times': self.capture_performed_times
        }


    @staticmethod
    @abstractmethod
    def comments_for_yaml_data():
        return {
            'main_comment': '任务上下文',
            'status': '任务状态',
            'counter': '计数器',
            'last_perform_time': '最后一次执行时间',
            'capture_performed_times': '抓取次数'
        }