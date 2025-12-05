__doc__="单个任务的rich终端面板块"
__author__="Li Qingyun"
__date__="2025-11-19"

from threading import Lock
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn, TimeRemainingColumn, ProgressColumn
from rich.text import Text
from itertools import cycle

from core.util.console.rich.rich_console import console
from core.util.console.rich.util.count_column import RichCountColumn


class BasicWebsiteTaskConsolePanel:
    """管理单个任务面板的显示和状态"""

    def __init__(self, task_name):
        """
        初始化任务面板
        :param task_name: 任务名称
        :param total_url_count: 该任务需要访问的URL总数
        """
        # 任务名
        self.task_name = task_name


        # 乐观锁, 保证只有一个线程可以进行写操作
        self._lock = Lock()

        # 1. 网站列表访问的进度
        ## 1.1 当前正在访问的url
        self._current_url = "等待开始..."
        ## 1.2 总url数量
        self._total_url_count = 0
        ## 1.3 已经访问过的url数量
        self._visited_url_count = 0

        # 2. 网站内访问次数的进度
        # 2.1 当前的url已访问的次数
        self._current_url_visited_times = 0
        # 2.2 当前url的最大访问次数
        self._current_url_total_visit_times = 1

        # 3. 所有任务是否完成
        self._all_tasks_finished = False


        # 创建网站列表进度条
        self.total_url_progress = Progress(
            TextColumn("[bold blue]网站列表进度:"),
            BarColumn(bar_width=30),  # 稍微减小宽度适应更多任务
            TaskProgressColumn(),
            TextColumn("({task.completed}/{task.total})")
        )
        self.url_task_name = self.total_url_progress.add_task(
            f"任务-{task_name}",
            total=self._total_url_count,
        )

        # 创建当前URL内访问次数进度条
        self.current_visited_times_progress = Progress(
            TextColumn("[bold green]URL访问:"),
            BarColumn(bar_width=30),
            RichCountColumn(),
            TextColumn("["),
            TaskProgressColumn(),
            TextColumn("]"),
        )
        self.current_url_visit_times_task_name = self.current_visited_times_progress.add_task(
            f"任务{task_name}-访问",
            total=1
        )

    def init(self,
             task_name,
             visited_url_count,
             total_url_count
             ):
        # 设置任务名, 已经访问过的网站数量, 总的网站数量
        self.task_name = task_name
        self._visited_url_count = visited_url_count
        self._total_url_count = total_url_count


    def start_new_url(self, url, current_visit_times, total_visit_times):
        """开始访问一个新的URL"""
        with self._lock:
            # 设置当前访问的url
            self._current_url = url

            # 如果没传入, 默认就是0
            self._current_url_visited_times = current_visit_times if current_visit_times is not None else 0
            self._current_url_total_visit_times = total_visit_times

            self.total_url_progress.update(
                self.url_task_name,
                total=self._total_url_count,
                completed=self._visited_url_count,
                description=f"访问 {url[:20]}..." if len(url) > 20 else f"访问 {url}"
            )

            self.current_visited_times_progress.update(
                self.current_url_visit_times_task_name,
                total=self._current_url_total_visit_times,
                completed=self._current_url_visited_times,
            )

    def finish_one_visit_in_website(self):
        """记录当前URL的一次访问"""
        with self._lock:
            if self._current_url_visited_times < self._current_url_total_visit_times:
                self._current_url_visited_times += 1
                self.current_visited_times_progress.update(self.current_url_visit_times_task_name, advance=1)

    def finish_one_website(self):
        """完成一个网站的访问"""
        with self._lock:
            if self._visited_url_count < self._total_url_count:
                self._visited_url_count += 1
                self.total_url_progress.update(self.url_task_name, advance=1)

                if self._visited_url_count >= self._total_url_count:
                    self._all_tasks_finished = True

    def set_all_finished(self):
        """设置所有任务为完成状态"""
        with self._lock:
            self._all_tasks_finished = True

    def is_all_finished(self):
        """检查所有任务是否完成"""
        return self._all_tasks_finished

    def get_renderable(self):
        """生成该任务面板的可渲染内容（优化内部间距）"""
        with self._lock:
            # 创建更紧凑的任务内容布局
            task_layout = Layout()

            # 使用更紧凑的布局，减少垂直空间占用
            task_layout.split_column(
                Layout(self.total_url_progress, name="site_progress", size=2),  # 从3减少到2
                Layout(Text(
                    f"URL: {self._current_url}",
                    style="bold yellow"), name="current_url", size=1),  # 从2减少到1
                Layout(self.current_visited_times_progress, name="url_progress", size=2)  # 从3减少到2
            )

            completion_pct = (self._visited_url_count / self._total_url_count * 100) if self._total_url_count > 0 else 0

            # 根据完成状态设置边框颜色
            if self.is_all_finished():
                border_style = "bold green"
                subtitle = "✅ 已完成"
            else:
                border_style = "bright_blue"
                subtitle = f"{completion_pct:.1f}%"

            return Panel(
                task_layout,
                title=f"[bold cyan]任务{self.task_name}[/bold cyan]",
                subtitle=subtitle,
                border_style=border_style,
                height=8,  # 从10减少到8，为行间间隔留出空间
                padding=(0, 1, 0, 1)  # 减少左右内边距，使用间隔代替
            )
