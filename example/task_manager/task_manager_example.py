__doc__ = "任务管理器使用示例"
__author__ = "Li Qingyun"
__date__ = "2025-03-17"

from core.task.task_manager.task_manager import TaskManager
from core.util import PathUtil
from core.util.io.log_util import LogUtil


# 项目根路径(建议使用在操作系统中的绝对路径)
__project_root_dir = '/Users/your_user_name/PycharmProjects/small_brother'


def __start_task_manager():
    """
    使用任务管理器执行任务
    """
    # 1. 设置任务组描述文件的路径
    task_group_file_path = PathUtil.dir_path_join(__project_root_dir, 'example/task_manager/task_group_example.yaml')
    # 2. 创建任务管理器
    task_manager = TaskManager(task_group_file_path=task_group_file_path)
    # 3. 开始执行任务
    task_manager.start_performing()



if __name__ == '__main__':
    # 设置日志
    LogUtil().enable_log = True
    LogUtil().set_log_dir(PathUtil.dir_path_join(__project_root_dir, 'example/task/website/output/log'))

    # 启动任务管理器
    __start_task_manager()
