__doc__="任务体(参考线程体, 是线程的包装, 本身不能执行)"
__author__="Li Qingyun"
__date__="2025-03-10"

from core.task.const.task_perform_status import TaskPerformStatus
from core.task.interface.task_thread import TaskThread


class Performable:
    def __init__(self,
                 task_name: str,
                 task_file_path: str,
                 task_perform_status: TaskPerformStatus,
                 ):

        # 任务名
        self.task_name = task_name
        # 任务文件路径
        self.task_file_path = task_file_path
        # 任务执行状态
        self.task_perform_status = task_perform_status
        # 任务线程
        self.task_thread = None

        self.create_task_thread()
        pass


    def start(self):
        self.task_thread.start()
        # self.task_thread.join()


    def stop(self):
        self.task_thread.stop()
        self.update_task_perform_status(TaskPerformStatus.INTERRUPT)
        self.task_thread.join()


    def update_task_perform_status(self, new_status: TaskPerformStatus):
        """
        更新任务执行状态
        :param new_status:
        :return:
        """
        self.task_perform_status = new_status
        pass


    def is_task_need_to_perform(self) -> bool:
        if self.task_thread.is_finished():
            return False
        return True

    def set_perform_status_finished(self):
        """
        设置任务执行状态为完成
        :return:
        """
        self.update_task_perform_status(TaskPerformStatus.FINISHED)


    def is_perform_finished(self) -> bool:
        """
        任务线程是否完成
        :return:
        """
        # 线程存活状态指示了线程是否结束
        if self.task_thread.is_alive() is False:
            return False
        else:
            self.set_perform_status_finished()
            return True


    def create_task_thread(self):
        """
        创建任务线程
        :return:
        """
        self.task_thread = TaskThread.create_task_thread_from_config_file(self.task_file_path)



    @staticmethod
    def from_dict(config_dict):
        task_name = config_dict.get('task_name')
        task_file_path = config_dict.get('task_file_path')
        task_perform_status = TaskPerformStatus(config_dict.get('status'))
        return Performable(task_name=task_name,
                           task_file_path=task_file_path,
                           task_perform_status=task_perform_status
                           )


    def to_dict(self):
        return {
            'task_name': self.task_name,
            'task_file_path': self.task_file_path,
            'status': self.task_perform_status.value
        }