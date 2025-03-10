__doc__='任务-抓取策略'
__author__='Li Qingyun'
__date__='2025-02-28'

from abc import abstractmethod


class TaskCapturePolicy:

    def __init__(self,
                 capture_times: int,
                 timeout: int=None,
                 visit_interval: int=0
                 ):
        self.capture_times = capture_times      # 抓取次数
        self.timeout = timeout                  # 超时时间
        self.visit_interval = visit_interval    # 访问间隔
        pass


    @staticmethod
    @abstractmethod
    def from_dict(config_dict):
        """解析capture_policy字典"""
        # 1. 抓取次数
        if config_dict.get('capture_times'):
            capture_times = config_dict.get('capture_times')
        else:
            raise ValueError('[TaskCapturePolicy] 没有 capture_times 字段')

        # 2. 获取timeout字段
        timeout = config_dict.get('timeout', None)

        # 3. 获取visit_interval字段
        visit_interval = config_dict.get('visit_interval', 0)

        return TaskCapturePolicy(capture_times=capture_times,
                                 timeout=timeout,
                                 visit_interval=visit_interval)


    @abstractmethod
    def to_dict(self):
        """转字典"""
        return {
            'capture_times': self.capture_times,
            'timeout': self.timeout,
            'visit_interval': self.visit_interval
        }


    @staticmethod
    @abstractmethod
    def comments_for_yaml_data():
        """
        yaml文件中的注释
        :return:
        """
        return {
            'main_comment': '抓取策略',
            'capture_times': '抓取次数',
            'timeout': '超时时间',
            'visit_interval': '访问间隔'
        }
