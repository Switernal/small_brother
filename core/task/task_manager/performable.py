__doc__="任务体(参考线程体, 是线程的包装, 本身不能执行)"
__author__="Li Qingyun"
__date__="2025-03-10"

from core.task.const.task_perform_status import TaskPerformStatus
from core.task.interface.task_progress import TaskProgress
from core.task.interface.task_thread import TaskThread


class Performable:
    """
    任务体
        任务体是任务的包装, 本身不能执行
        任务体内存了 TaskThread 线程对象, 通过 Performable 来控制任务进程
        可以更好的多任务并行和对任务执行状态进行监控
    """
    def __init__(self,
                 task_name: str,
                 task_file_path: str,
                 task_perform_status: TaskPerformStatus,
                 ):
        """

        :param task_name:           任务名
        :param task_file_path:      任务文件路径
        :param task_perform_status: 任务体执行状态
        """

        # 初始化变量
        # 1. 任务名
        self.task_name = task_name
        # 2. 任务文件路径
        self.task_file_path = task_file_path
        # 3. 任务执行状态
        self.task_perform_status = task_perform_status

        # 运行时变量
        # 1. 任务线程
        self.task_thread = None

        self.create_task_thread()
        pass


    def start(self):
        """
        启动任务
        :return:
        """
        self.task_thread.start()
        # self.task_thread.join()


    def stop(self):
        """
        停止任务
        :return:
        """
        self.task_thread.stop()
        self.update_task_perform_status(TaskPerformStatus.INTERRUPT)
        self.task_thread.join()


    def create_task_thread(self):
        """
        创建任务线程
        :return:
        """
        self.task_thread = TaskThread.create_task_thread_from_config_file(self.task_file_path)


    def fetch_task_progress(self) -> TaskProgress:
        """
        获取任务执行进度(暂时没用)
        :return:
        """
        return self.task_thread.task_progress


    def update_task_perform_status(self, new_status: TaskPerformStatus):
        """
        更新任务执行状态
        :param new_status:
        :return:
        """
        self.task_perform_status = new_status
        pass


    def is_task_need_to_perform(self) -> bool:
        """
        判断任务是否需要执行(如果任务的状态是已经完成, 就不需要执行)
            此状态不是线程状态,是任务状态
        :return:
        """
        if self.task_thread.is_finished():
            return False
        return True


    def set_task_perform_status_finished(self):
        """
        设置任务执行状态为完成
        :return:
        """
        self.update_task_perform_status(TaskPerformStatus.FINISHED)


    def is_perform_finished(self) -> bool:
        """
        任务线程是否执行完成
        :return:
        """
        # 线程存活状态指示了线程是否结束
        if self.task_thread.is_alive() is True:
            return False
        else:
            self.set_task_perform_status_finished()
            return True



    @staticmethod
    def from_dict(config_dict):
        """
        从字典中创建对象
        :param config_dict:
        :return:
        """
        task_name = config_dict.get('task_name')
        task_file_path = config_dict.get('task_file_path')
        task_perform_status = TaskPerformStatus(config_dict.get('status'))
        return Performable(task_name=task_name,
                           task_file_path=task_file_path,
                           task_perform_status=task_perform_status
                           )


    def to_dict(self):
        """
        转字典
        :return:
        """
        return {
            'task_name': self.task_name,
            'task_file_path': self.task_file_path,
            'status': self.task_perform_status.value
        }