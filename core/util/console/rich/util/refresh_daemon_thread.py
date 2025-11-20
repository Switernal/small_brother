__doc__="Rich 刷新守护进程"
__author__="Li Qingyun"
__date__="2025-11-20"

import time

from rich.live import Live

from core.util.multithreading import BetterThread
from core.util.console.rich.rich_console import console


class RefreshDaemonThread(BetterThread):
    """
    Rich 刷新守护进程线程
    """

    def __init__(self,
                 listen_thread: BetterThread,
                 refresh_function,
                 refresh_per_second: int = 1
                 ):
        """
        构造函数
        :param refresh_function: 刷新函数
        :param refresh_interval: 刷新间隔，单位秒
        """
        super().__init__(name="RichRefreshDaemonThread", daemon=True)

        # 1. 监听线程, 如果这个线程结束, 则自己也结束
        self.listen_thread = listen_thread

        # 2. 刷新函数
        self.refresh_function = refresh_function
        # 3. 每秒刷新次数
        self.refresh_per_second = refresh_per_second


    def run(self):
        """
        线程运行函数
        :return:
        """
        # 使用Live显示实时界面
        with Live(self.refresh_function(), refresh_per_second=self.refresh_per_second, screen=False) as live:  # 降低刷新率
            while self.listen_thread.is_alive():
                # 实时更新界面
                live.update(self.refresh_function())
                time.sleep(0.15)  # 增加睡眠时间减少CPU占用

            # 工作完成后显示最终状态
            console.print("\n[bold green]✅ 所有任务已完成![/bold green]")


    def clear(self):
        pass
