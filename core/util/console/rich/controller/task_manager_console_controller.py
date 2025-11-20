__doc__="rich-任务管理器-控制器"
__author__="Li Qingyun"
__date__="2025-11-19"


from threading import Lock

from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn

from core.util.console.rich.util.refresh_daemon_thread import RefreshDaemonThread


class TaskManagerConsoleController:
    """任务管理器，负责全局进度和所有任务面板"""

    def __init__(self, task_manager_thread):
        # 并发锁
        self.lock = Lock()

        # 1. 任务数量
        self.task_count = 0

        # 2. 任务面板列表 {task_name: task_panel}
        self.task_panels = {}

        # 3. 存储一个task_manager线程的对象, 用于判断线程执行器是否存活
        self.task_manager_thread = task_manager_thread

        # 4. 启一个守护线程, 用于持续刷新终端界面
        self.refresh_daemon_thread = None

        # 创建全局进度条(任务完成的进度)
        self.overall_progress = Progress(
            TextColumn("[bold]任务执行进度:"),
            BarColumn(bar_width=50),
            TaskProgressColumn(),
            TextColumn("({task.completed}/{task.total})")
        )

        # 添加总体任务
        self.overall_task_id = None



    def init(self, task_panel_list):
        """
        初始化任务管理器
        :param task_panel_list: 任务面板列表
        """
        # 任务数量
        self.task_count = len(task_panel_list)
        # 任务面板对象列表
        self.task_panels = task_panel_list

        # 创建任务管理器的总进度条
        self.overall_task_id = self.overall_progress.add_task(
            "所有任务",
            total=self.task_count
        )

    def start_refresh(self):
        """
        启动终端界面刷新守护线程
        """
        self.refresh_daemon_thread = RefreshDaemonThread(listen_thread=self.task_manager_thread,
                                                         refresh_function=self.get_layout,
                                                         refresh_per_second=1
                                                         )
        self.refresh_daemon_thread.start()


    def finish_one_task(self, advance=1):
        """更新全局进度条"""
        self.overall_progress.update(self.overall_task_id, advance=advance)


    def get_layout(self):
        """生成完整的终端界面布局"""
        layout = Layout()

        # 分割为顶部（全局进度）和底部（任务面板）
        layout.split_column(
            Layout(
                Panel(self.overall_progress, title="[bold red]全局任务进度[/bold red]"),
                name="header",
                size=5
            ),
            Layout(name="tasks")
        )

        # 底部进一步水平分割为多个任务面板
        task_layouts = []
        for panel in self.task_panels:
            task_layouts.append(Layout(panel.get_renderable(), minimum_size=35))  # 稍微增加最小尺寸

        layout["tasks"].split_row(*task_layouts)

        return layout
