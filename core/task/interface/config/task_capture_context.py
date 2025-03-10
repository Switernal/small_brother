__doc__='任务-上下文'
__author__='Li Qingyun'
__date__='2025-02-28'

import enum
from abc import abstractmethod


class TaskStatus(enum.Enum):
    """
    任务状态
    """
    INITIAL = 'initial'     # 初始状态
    RESUME = 'resume'       # 恢复状态
    RUNNING = 'running'     # 运行中
    FINISHED = 'finished'   # 完成
    INTERRUPT_UNEXPECT = 'unexpect_interrupt'   # 意外中断
    INTERRUPT_MANUAL = 'manual_interrupt'       # 手动中断

    def __str__(self):
        return self.value



class TaskCaptureContext:

    def __init__(self,
                 status: TaskStatus,
                 counter: int,
                 last_perform_time,
                 capture_performed_times
                 ):
        self.status = status                                        # 任务状态
        self.counter = counter                                      # 计数器
        self.last_perform_time = last_perform_time                  # 最后一次执行时间
        self.capture_performed_times = capture_performed_times      # 抓取次数
        pass

    def increase_counter(self):
        """计数器增加"""
        self.counter += 1
        pass

    def update_counter(self, new_counter):
        """修改计数器"""
        self.counter = new_counter
        pass

    def update_status(self, new_status: TaskStatus):
        """修改状态"""
        self.status = new_status
        pass

    def update_last_perform_time(self, new_time):
        """更新最后一次执行时间"""
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

        print(f'counter: {counter}')

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