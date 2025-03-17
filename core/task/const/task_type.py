__doc__="任务类型"
__author__="Li Qingyun"
__date__="2025-03-10"

import enum


class TaskType(enum.Enum):
    """
    任务类型 (用于描述任务类型)
        后续可加入多种自定义类型扩展
        建议类型为大类别, 比如 website/dns/application 等, 细分类别可以放到 RequestType 里去
        不过其实这个字段似乎用处也不大, 日后考虑废弃, 仅使用 RequestType
    """

    WEBSITE_SINGLE_TAB = "website_single_tab"   # 单标签网页
    WEBSITE_MULTI_TAB = "website_multi_tab"     # 多标签网页
    APPLICATION = "application"                 # 应用 (todo: 尚未实现)
    UNKNOWN = 'unknown'                         # 未知

    def __str__(self):
        return self.value