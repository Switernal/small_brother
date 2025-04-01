__doc__ = "网站单标签任务示例"
__author__ = "Li Qingyun"
__date__ = "2025-03-17"

import os
import sys
sys.path.append(os.getcwd())

from core.task.impl.website.single_tab.website_single_tab_task_thread import WebsiteSingleTabTaskThread
from core.util import PathUtil
from core.util.io.log_util import LogUtil

# 项目根路径(建议使用在操作系统中的绝对路径)
__project_root_dir = '/Users/your_user_name/PycharmProjects/small_brother'


def __perform_direct_task():
    """
    执行直连测试任务
    """
    print('开始执行直连测试任务')
    # 1. 设置 task 描述文件的路径
    task_description_path = PathUtil.dir_path_join(__project_root_dir,
                                                   'example/task/website/task_description_example/TaskDescription-test_task_direct.yaml')
    # 2. 使用描述文件创建任务线程
    task = WebsiteSingleTabTaskThread.create_task_from_config_file(task_config_file_path=task_description_path)
    # 3. 启动任务线程
    task.start()
    task.join()     # 阻塞执行


def __perform_proxy_task():
    """
    执行代理测试任务
    """
    print('开始执行代理测试任务')
    task_description_path = PathUtil.dir_path_join(__project_root_dir,
                                                   'example/task/website/task_description_example/TaskDescription-test_task_proxy.yaml')
    task = WebsiteSingleTabTaskThread.create_task_from_config_file(task_config_file_path=task_description_path)
    task.start()
    task.join()


if __name__ == '__main__':
    # 设置日志
    LogUtil().enable_log = True  # 是否启用日志
    LogUtil().set_log_dir(PathUtil.dir_path_join(__project_root_dir, 'example/task/website/output/log'))  # 日志目录

    # 注: 如果网站列表过长, 任务执行会很久, 建议仅使用少量网站列表进行测试

    # 1. 执行直连测试任务
    __perform_direct_task()

    # 2. 执行代理测试任务
    __perform_proxy_task()
