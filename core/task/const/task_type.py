__doc__="任务类型"
__author__="Li Qingyun"
__date__="2025-03-10"

import enum


class TaskType(enum.Enum):
    """
    任务类型
    """

    WEBSITE_SINGLE_TAB = "website_single_tab"
    WEBSITE_MULTI_TAB = "website_multi_tab"
    APPLICATION = "application"                 # todo: 尚未实现
    UNKNOWN = 'unknown'

    def __str__(self):
        return self.value