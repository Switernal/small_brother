__doc__="任务类型"
__author__="Li Qingyun"
__date__="2025-03-10"

import enum


class TaskType(enum.Enum):
    """
    任务类型
    """

    WEBSITE_SINGLE_TAB = "website_single_tab"   # 单标签网页
    WEBSITE_MULTI_TAB = "website_multi_tab"     # 多标签网页
    APPLICATION = "application"                 # 应用 (todo: 尚未实现)
    UNKNOWN = 'unknown'                         # 未知

    def __str__(self):
        return self.value