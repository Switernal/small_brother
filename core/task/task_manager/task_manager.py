__doc__="任务管理器"
__author__="Li Qingyun"
__date__="2025-03-10"

import signal
import threading
from time import sleep

from tqdm import tqdm

from core.task.task_manager.performable import Performable
from core.util.io.log_util import LogUtil
from core.util.io.yaml_util import YamlUtil


class TaskManager:
    """
    任务管理器
        任务管理器是一个任务组的管理器, 负责管理任务组中的所有任务
        任务组描述文件是一个yaml文件, 包含了任务组的信息, 并发设置等
    """
    def __init__(self, task_group_file_path: str):
        """

        :param task_group_file_path: 任务组文件路径
        """

        # 任务组文件路径
        self.task_group_file_path = task_group_file_path

        self.task_group_name = None
        self.task_group_note = None
        # 最大同时线程量
        self.max_concurrent_num = 1


        # 下一个要执行的index
        self.next_task_to_perform_index = 0
        # 任务列表
        self.performable_list = []
        # 执行中的任务列表(index列表)
        self.performing_index_list = set()


        # 停止信号
        self._stop_event = threading.Event()
        # 注册系统事件, 监听中断信号
        signal.signal(signal.SIGINT, self.handle_interrupt)

        self.init_task_manager()
        pass



    def start_performing(self):
        """
        开始执行
        :return:
        """
        with tqdm(total=len(self.performable_list),
                  initial=self.next_task_to_perform_index,
                  desc="任务管理器进度",
                  unit='个任务',
                  position=1) as progress_bar:

            progress_bar.display()

            while self._stop_event.is_set() is False:
                # 还有没执行的线程
                if self.next_task_to_perform_index < len(self.performable_list):
                    # 如果没达到最大并发数, 就开始执行
                    if self.__num_of_running_threads() < self.max_concurrent_num:
                        # 如果任务的状态是已完成(非线程状态), 就直接跳过
                        if not self.performable_list[self.next_task_to_perform_index].is_task_need_to_perform():
                            LogUtil().debug('main', f"任务 {self.performable_list[self.next_task_to_perform_index].task_name} 已完成")
                            self.performable_list[self.next_task_to_perform_index].set_task_perform_status_finished()
                            self.next_task_to_perform_index += 1
                            progress_bar.update(1)  # 当做一个任务完成, 进度直接+1
                            continue
                        # 取一个开始执行
                        self.performing_index_list.add(self.next_task_to_perform_index)
                        self.performable_list[self.next_task_to_perform_index].start()
                        self.next_task_to_perform_index += 1
                else:
                    # 所有线程都在运行状态了
                    # 所有任务都执行完了
                    if self.__num_of_running_threads() == 0:
                        # 跳出循环
                        break
                    # 还有没执行完的
                    remove_set = set()
                    for index in self.performing_index_list:
                        # 如果线程不再存活, 就说明终止了
                        if self.performable_list[index].is_perform_finished():
                            # 添加到需要清除的列表
                            remove_set.add(index)
                    # 如果有需要被移除的index, 就遍历一下全部移除
                    if len(remove_set) > 0:
                        for index_to_remove in remove_set:
                            self.performing_index_list.remove(index_to_remove)
                            progress_bar.update(1)  # 一个任务完成, 进度才能+1

                # 每次循环更新, 就存一下
                self.save_task_group_to_disk()
                # 防止刷新过快
                sleep(5)

            # end while
        # end with tqdm

        # 走到这里有两种情况: 1. 中断信号  2. 全部完成
        # 1. 执行中断
        if self._stop_event.is_set():
            self.stop_all_task()
            LogUtil().debug('main', "[TaskManager] 任务执行中断")
            return

        # 2. 全部完成
        LogUtil().debug('main', "[TaskManager] 所有任务已全部执行完毕")



    def stop_all_task(self):
        """
        停止所有执行中的任务
        :return:
        """
        LogUtil().debug('main', "[TaskManager] 正在通知任务全部停止...")
        if len(self.performing_index_list) == 0:
            return
        # 通知执行中的所有任务
        for index in self.performing_index_list:
            self.performable_list[index].stop()
        LogUtil().debug('main', "[TaskManager] 任务已全部停止")
        # 保存一下
        self.save_task_group_to_disk()


    def handle_interrupt(self, signum, frame):
        LogUtil().debug('main', "[TaskManager] 收到系统中断消息")
        self._stop_event.set()
        # exit(0)


    def __num_of_running_threads(self):
        """
        运行中的线程数量
        :return:
        """
        return len(self.performing_index_list)


    def init_task_manager(self):
        """
        从文件中创建任务管理器
        :return:
        """
        config_dict = YamlUtil().load(self.task_group_file_path)

        # 1. 获取名字
        if config_dict.get("task_group_name"):
            self.task_group_name = config_dict.get("task_group_name")
        else:
            raise ValueError("[TaskManager] 任务组文件缺少name字段")

        # 2. 获取备注
        if config_dict.get("task_group_note"):
            self.task_group_note = config_dict.get("task_group_note")
        else:
            raise ValueError("[TaskManager] 任务组文件缺少note字段")

        # 3. 获取最大并发数
        self.max_concurrent_num = config_dict.get("max_concurrent_num", 1)

        # 4. 循环创建Performable
        performable_dict_list = config_dict.get("task_list")
        for performable_dict in performable_dict_list:
            self.performable_list.append(Performable.from_dict(performable_dict))



    def save_task_group_to_disk(self):
        """
        保存任务组信息到磁盘
        :return:
        """
        config_dict = {
            "task_group_name": self.task_group_name,
            "task_group_note": self.task_group_note,
            "max_concurrent_num": self.max_concurrent_num,
            "task_list": [performable.to_dict() for performable in self.performable_list]
        }
        commented_yaml_data = YamlUtil().add_cycle_comments(config_dict, self.get_comment_for_yaml_data())
        YamlUtil().dump_with_comments(commented_yaml_data, self.task_group_file_path)



    def get_comment_for_yaml_data(self):
        """
        获取yaml数据的注释
        :return:
        """
        return {
            "task_group_name": "任务组名",
            "task_group_note": "任务组备注",
            "max_concurrent_num": "最大并发数",
            "task_list": "任务列表"
        }