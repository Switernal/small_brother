__doc__="任务执行状态(该状态仅用于TaskManager管理使用, 区别于任务内状态 TaskType 类)"
__author__="Li Qingyun"
__date__="2025-03-10"

import enum


class TaskPerformStatus(enum.Enum):
    """
    任务执行状态 (仅用于TaskManager管理使用)
    """

    STANDBY = "standby"         # 准备执行
    PERFORMING = "performing"   # 正在执行
    INTERRUPT = "interrupt"     # 中断
    FINISHED = "finished"       # 已完成

    def __str__(self):
        return self.value