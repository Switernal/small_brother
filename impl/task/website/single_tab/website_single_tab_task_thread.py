__doc__="单标签网页任务线程"
__author__="Li Qingyun"
__date__="2025-03-10"


from time import sleep

from tqdm import tqdm

from core.task.interface.config.task_capture_context import TaskStatus
from core.task.interface.task_thread import TaskThread
from core.util.data_loader.website_list_data_loader import WebsiteListDataLoader
from core.util.io.yaml_util import YamlUtil
from core.util.string.time_util import TimeUtil
from impl.capture.website.website_single_tab_capture_thread import WebsiteSingleTabCaptureThread
from impl.task.website.single_tab.website_single_tab_task_config import WebsiteSingleTabTaskConfig


class WebsiteSingleTabTaskThread(TaskThread):

    def __init__(self,
                 task_config_file_path: str
                 ):
        super().__init__(
            task_config_file_path=task_config_file_path,
            name="WebsiteSingleTabTaskThread"
        )
        # 创建配置
        self.task_config = None
        # 初始化配置
        self.initial_task_from_config_file()

        # 任务相关变量
        self.website_list_dataloader = None
        pass

    def run(self):
        self.perform_task()
        pass

    def stop(self):
        super().stop()
        self.clear()


    def perform_task(self):
        """
        开始执行任务的操作, 需要在run中执行
        :return:
        """
        # 1. 判断是否完成
        if self.is_finished() is False:
            # 1.1 恢复上下文
            self.recover_from_context()
            # 1.2 从中断位置继续执行任务(循环阻塞)
            self.continue_perform()
        else:
            print(f'[WebsiteSingleTabTaskThread] 任务 {self.task_config.task_name} 已完成, 无需执行')

        # 2. 结束任务流程
        self.finalize()
        pass


    def task_being_interrupted(self):
        """
        停止标志位设置后, 需要调用这个
        :return:
        """
        # 1. 更新任务状态为手动中断
        self.task_config.capture_context.update_status(TaskStatus.INTERRUPT_MANUAL)
        # 2. 更新任务最后执行时间
        self.task_config.capture_context.update_last_perform_time(TimeUtil.now_time_str())
        # 3. 保存任务配置到磁盘
        self.save_config_to_disk()
        print(f'[WebsiteSingleTabTaskThread] 任务手动中断: {self.task_config.task_name}')
        pass


    def finalize(self):
        # 1. 更新任务状态为已完成
        self.task_config.capture_context.update_status(TaskStatus.FINISHED)
        # 2. 更新任务最后执行时间
        self.task_config.capture_context.update_last_perform_time(TimeUtil.now_time_str())
        # 3. 保存任务配置到磁盘
        self.save_config_to_disk()

        print(f'[WebsiteSingleTabTaskThread] 任务完成: {self.task_config.task_name}')

        self.clear()
        pass


    def initial_task_from_config_file(self):
        """初始化任务"""
        self.task_config = WebsiteSingleTabTaskConfig.create_task_config_from_file(self.task_config_file_path)


    def recover_from_context(self):
        """
        从上下文中恢复任务
        :return:
        """
        # 1. 载入网站列表数据
        self.website_list_dataloader  = WebsiteListDataLoader(self.task_config.website_list_path)

        # 2. 先看网站计数器是否为0, 如果计数器不为0, 先定位到那个行
        counter = self.task_config.capture_context.counter
        if counter > 0:
            # 从上下文中获取上一次执行到第几个网站, 读取网站列表, 定位到那个网站
            self.website_list_dataloader.seek_to_line(counter)


    def continue_perform(self):
        """
        继续执行任务, 循环阻塞
        :return:
        """
        print(f'[WebsiteSingleTabTaskThread] 开始执行任务 {self.task_config.task_name}')
        # 1. 更新任务状态为手动中断
        if self.task_config.capture_context.status == TaskStatus.INITIAL:
            self.task_config.capture_context.update_status(TaskStatus.RUNNING)
        else:
            self.task_config.capture_context.update_status(TaskStatus.RESUME)


        # 从定位的网站遍历网站列表
        while self.website_list_dataloader.is_finish() is False:  # 读取未结束的情况下
            # 0. 检查停止标志
            if self.stop_event.is_set():
                # 如果有终止信号, 就停止任务
                self.task_being_interrupted()
                return

            # 1. 当前的 url
            now_url = self.website_list_dataloader.read_line()
            print(f'[WebsiteSingleTabTaskThread] 当前网站: {now_url}')

            # 2. 如果context中已经抓取的次数没有达到达到了policy中的次数, 就执行
            if self.task_config.capture_context.capture_performed_times < self.task_config.capture_policy.capture_times:

                # 2.1 计算当前网站剩余抓取次数
                capture_times_left = self.task_config.capture_policy.capture_times - \
                                     self.task_config.capture_context.capture_performed_times
                # 2.2 循环抓取
                for capture_num in tqdm(range(1, capture_times_left + 1),
                                        desc=f"[WebsiteCaptureTask] 抓取网站 {now_url}",
                                        unit="次"):
                    # 4.1 检查终止信号
                    if self.stop_event.is_set():
                        # 如果有终止信号, 就停止任务
                        self.task_being_interrupted()
                        return

                    print(f'[WebsiteSingleTabTaskThread] 创建抓取任务')

                    # 4.2 创建抓取任务并执行
                    if self.task_config.extension_config is not None:
                        extension_config_dict = self.task_config.extension_config.config_dict
                    else:
                        extension_config_dict = None

                    if self.task_config.request_config is not None:
                        request_config_dict = self.task_config.request_config.config_dict
                    else:
                        request_config_dict = None

                    capture_thread = WebsiteSingleTabCaptureThread(
                        thread_name=f'{now_url}',
                        url=now_url,
                        output_main_dir=self.task_config.output_dir,
                        extension_config=extension_config_dict,
                        request_config=request_config_dict,
                        # sniffer_scapy_config=self.task_config.sniffer_scapy_config,
                        # sniffer_conn_tracker_config=self.task_config.sniffer_conn_tracker_config
                    )
                    print(f'[WebsiteSingleTabTaskThread] 启动抓取流程')
                    # 启动抓取流程
                    capture_thread.start()
                    print(f'[WebsiteSingleTabTaskThread] 抓取流程结束')
                    # 阻塞等待执行结束
                    capture_thread.join()

                    # 抓取一次完成后, 更新上下文, 并保存任务描述文件到磁盘
                    self.task_config.capture_context.increase_capture_performed_times()
                    self.save_config_to_disk()

                    sleep(30)
                    pass
                # end for capture_num (抓完一个网站了)

            # 移到下一个网站
            self.website_list_dataloader.move_next_line()

            # 更新上下文
            self.task_config.capture_context.update_counter(self.website_list_dataloader.current_line)
            self.task_config.capture_context.update_last_perform_time(TimeUtil.now_time_str())
            # 清空上下文中网站的抓取次数
            self.task_config.capture_context.clear_capture_performed_times()

            # 保存一下任务
            self.save_config_to_disk()

        # end while
        pass


    def save_config_to_disk(self):
        """
        保存任务到磁盘
        :return:
        """
        with open(self.task_config_file_path, 'w', encoding='utf-8') as file:
            YamlUtil().dump_with_comments(
                data=self.task_config.convert_to_commented_yaml_data(),
                file=file
            )


    def clear(self):
        pass
