__doc__='时间工具类'
__author__='Li Qingyun'
__date__='2025-03-09'

import datetime


class TimeUtil:
    @staticmethod
    def now_time_str():
        """
        获取当前时间的字符串, 格式: %Y-%m-%d_%H-%M-%S

        :return: 当前时间的字符串
        """
        return str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))