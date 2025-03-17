__doc__="任务状态(该状态用于描述任务内状态, 区别于 TaskPerformStatus 类)"
__author__="Li Qingyun"
__date__="2025-02-28"

import enum


class TaskStatus(enum.Enum):
    """
    任务状态 (该状态用于描述任务内状态, 区别于 TaskPerformStatus 类)
    """
    INITIAL = 'initial'     # 初始状态
    RESUME = 'resume'       # 恢复状态
    RUNNING = 'running'     # 运行中
    FINISHED = 'finished'   # 完成
    INTERRUPT = 'interrupt'   # 意外中断

    def __str__(self):
        return self.value