__doc__="任务执行进度"
__author__="Li Qingyun"
__date__="2025-03-13"


class TaskProgress:
    def __init__(self, current_progress: int, total_progress: int):
        self.current_progress = current_progress
        self.total_progress = total_progress
        pass

    def set_total_progress(self, total_progress: int):
        """
        设置总进度
        :param total_progress: 总进度
        :return:
        """
        self.total_progress = total_progress

    def update_current_progress(self, current_progress: int):
        """
        设置当前进度
        :param current_progress: 当前进度
        :return:
        """
        self.current_progress = current_progress


    def __str__(self):
        return f"TaskProgress: {self.current_progress}/{self.total_progress}"