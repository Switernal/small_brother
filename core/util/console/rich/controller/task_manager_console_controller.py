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
        """生成完整的界面布局，支持网格状排列并添加面板间距"""
        layout = Layout()

        # 分割为顶部（全局进度）和底部（任务区域）
        layout.split_column(
            Layout(
                Panel(self.overall_progress, title="[bold red]全局任务进度[/bold red]"),
                name="header",
                size=5
            ),
            Layout(name="tasks")
        )

        # 获取任务面板列表
        panels = self.task_panels
        num_tasks = len(panels)

        if num_tasks == 0:
            layout["tasks"].update(Layout(Panel("暂无任务", style="red")))
            return layout

        # 计算需要多少行：最多4行
        max_rows = 4
        max_cols = 3
        num_rows = min(max_rows, (num_tasks + max_cols - 1) // max_cols)

        # 创建行布局列表
        rows = []

        for row in range(num_rows):
            # 创建行布局
            row_layout = Layout(name=f"row_{row}")

            # 准备该行的单元格（包括间隔）
            cells = []
            for col in range(max_cols):
                task_index = row * max_cols + col

                # 在每列之间添加间隔（除了第一列之前）
                if col > 0:
                    # 添加间隔占位符，宽度为终端宽度的2%
                    cells.append(Layout("", ratio=2, minimum_size=3, visible=False))

                if task_index < num_tasks:
                    # 有任务：创建任务面板
                    cell_content = panels[task_index].get_renderable()
                    # 为每个任务面板创建容器布局，添加内边距
                    task_container = Layout(
                        cell_content,
                        ratio=8,  # 面板本身的比例权重
                        minimum_size=28  # 稍微减小最小尺寸为间隔留出空间
                    )
                    cells.append(task_container)
                else:
                    # 空位：创建空白占位符
                    cells.append(Layout("", ratio=8, minimum_size=28, visible=False))

            # 将行进行水平分割
            if cells:
                row_layout.split_row(*cells)

            # 在每行之间添加垂直间隔（除了第一行之前）
            if row > 0:
                # 添加垂直间隔行，高度为1行
                vertical_gap = Layout("", size=1, visible=False)
                rows.append(vertical_gap)

            rows.append(row_layout)

        # 将任务区域垂直分割为多行（包括间隔行）
        if rows:
            # 设置任务区域的总高度
            task_area_height = num_rows * 11 + (num_rows - 1)  # 每行11行高度 + 行间间隔
            layout["tasks"].update(Layout(name="task_container", size=task_area_height))
            layout["tasks"].split_column(*rows)
        else:
            layout["tasks"].update(Layout(Panel("无任务", style="red")))

        return layout
