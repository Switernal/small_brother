import time
import random
from threading import Thread, Lock
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn, TimeRemainingColumn, ProgressColumn
from rich.text import Text
from itertools import cycle

console = Console()


class CountColumn(ProgressColumn):
    """自定义列，显示完成次数/总次数"""

    def render(self, task) -> Text:
        """渲染次数显示：已完成/总数"""
        if task.total and task.total > 0:
            return Text(f"{int(task.completed)}/{int(task.total)}", style="progress.percentage")
        return Text("?")


class SingleTaskPanel:
    """管理单个任务面板的显示和状态"""

    def __init__(self, task_id, total_sites):
        self.task_id = task_id
        self.total_sites = total_sites
        self.lock = Lock()

        # 当前状态
        self.current_url = "等待开始..."
        self.sites_visited = 0
        self.current_url_visits = 0
        self.current_url_max_visits = 1
        self.all_tasks_completed = False

        # 创建网站进度条
        self.site_progress = Progress(
            TextColumn("[bold blue]网站进度:"),
            BarColumn(bar_width=30),  # 稍微减小宽度适应更多任务
            TaskProgressColumn(),
            TextColumn("({task.completed}/{task.total})")
        )
        self.site_task_id = self.site_progress.add_task(
            f"任务{task_id}",
            total=total_sites
        )

        # 创建URL访问进度条
        self.url_visit_progress = Progress(
            TextColumn("[bold green]URL访问:"),
            BarColumn(bar_width=30),
            CountColumn(),
            TextColumn("["),
            TaskProgressColumn(),
            TextColumn("]"),
        )
        self.url_visit_task_id = self.url_visit_progress.add_task(
            f"任务{task_id}-访问",
            total=1
        )

    def start_new_url(self, url, max_visits):
        """开始访问一个新的URL"""
        with self.lock:
            self.current_url = url
            self.current_url_visits = 0
            self.current_url_max_visits = max_visits

            self.url_visit_progress.update(
                self.url_visit_task_id,
                total=max_visits,
                completed=0,
                description=f"访问 {url[:20]}..." if len(url) > 20 else f"访问 {url}"
            )

    def record_url_visit(self):
        """记录当前URL的一次访问"""
        with self.lock:
            if self.current_url_visits < self.current_url_max_visits:
                self.current_url_visits += 1
                self.url_visit_progress.update(self.url_visit_task_id, advance=1)

    def complete_site(self):
        """完成一个网站的访问"""
        with self.lock:
            if self.sites_visited < self.total_sites:
                self.sites_visited += 1
                self.site_progress.update(self.site_task_id, advance=1)

                if self.sites_visited >= self.total_sites:
                    self.all_tasks_completed = True

    def is_all_completed(self):
        """检查所有任务是否完成"""
        return self.all_tasks_completed

    def get_renderable(self):
        """生成该任务面板的可渲染内容（优化内部间距）"""
        with self.lock:
            # 创建更紧凑的任务内容布局
            task_layout = Layout()

            # 使用更紧凑的布局，减少垂直空间占用
            task_layout.split_column(
                Layout(self.site_progress, name="site_progress", size=2),  # 从3减少到2
                Layout(Text(
                    f"URL: {self.current_url[:20]}..." if len(self.current_url) > 20 else f"URL: {self.current_url}",
                    style="bold yellow"), name="current_url", size=1),  # 从2减少到1
                Layout(self.url_visit_progress, name="url_progress", size=2)  # 从3减少到2
            )

            completion_pct = (self.sites_visited / self.total_sites * 100) if self.total_sites > 0 else 0

            # 根据完成状态设置边框颜色
            if self.is_all_completed():
                border_style = "bold green"
                subtitle = "✅ 已完成"
            else:
                border_style = "bright_blue"
                subtitle = f"{completion_pct:.1f}%"

            return Panel(
                task_layout,
                title=f"[bold cyan]任务{self.task_id:02d}[/bold cyan]",
                subtitle=subtitle,
                border_style=border_style,
                height=8,  # 从10减少到8，为行间间隔留出空间
                padding=(0, 1, 0, 1)  # 减少左右内边距，使用间隔代替
            )


class TaskManager:
    """任务管理器，支持最多12个任务"""

    def __init__(self, max_concurrent_tasks=12, sites_per_task=5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.sites_per_task = sites_per_task
        self.lock = Lock()
        self.task_panels = []

        # 创建全局进度条
        self.overall_progress = Progress(
            TextColumn("[bold]总体进度:"),
            BarColumn(bar_width=50),
            TaskProgressColumn(),
            TextColumn("({task.completed}/{task.total})")
        )
        self.overall_task_id = self.overall_progress.add_task(
            "所有任务",
            total=max_concurrent_tasks * sites_per_task
        )

        # 初始化任务面板（最多12个）
        for i in range(min(max_concurrent_tasks, 12)):  # 确保不超过12个
            self.task_panels.append(SingleTaskPanel(i + 1, sites_per_task))

    def update_overall_progress(self, advance=1):
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


def simulate_workload(task_manager):
    """模拟工作负载，支持最多12个任务"""
    import random

    # 为每个任务创建模拟的网站URL列表
    websites = []
    for task_num in range(len(task_manager.task_panels)):
        task_websites = [f"https://site-{task_num}-{i}.com" for i in range(task_manager.sites_per_task)]
        websites.append(task_websites)

    # 模拟多个任务同时进行
    threads = []
    for task_num in range(len(task_manager.task_panels)):
        thread = Thread(target=simulate_single_task,
                        args=(task_manager, task_num, websites[task_num]))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # 等待所有任务完成
    for thread in threads:
        thread.join()


def simulate_single_task(task_manager, task_num, websites):
    """模拟单个任务的执行"""
    task_panel = task_manager.task_panels[task_num]

    for site_url in websites:
        # 开始访问新网站
        max_visits = random.randint(3, 8)
        task_panel.start_new_url(site_url, max_visits)

        # 模拟多次访问当前URL
        for visit in range(max_visits):
            task_panel.record_url_visit()
            time.sleep(0.1 + random.random() * 0.2)  # 减少延迟适应更多任务

        # 完成一个网站
        task_panel.finish_one_website()
        task_manager.finish_one_task()

        time.sleep(0.3)  # 减少网站间延迟


def main():
    """主函数"""
    console.clear()
    console.print(f"[bold green]🚀 启动高级任务监控系统（支持最多12个并发任务）[/bold green]")

    # 创建任务管理器：支持最多12个并发任务
    task_manager = TaskManager(max_concurrent_tasks=10, sites_per_task=21)

    console.print(f"[yellow]已创建 {len(task_manager.task_panels)} 个任务面板[/yellow]")

    # 创建模拟工作线程
    work_thread = Thread(target=simulate_workload, args=(task_manager,))
    work_thread.daemon = True
    work_thread.start()

    # 使用Live显示实时界面
    with Live(task_manager.get_layout(), refresh_per_second=1, screen=False) as live:  # 降低刷新率
        try:
            while work_thread.is_alive():
                # 实时更新界面
                live.update(task_manager.get_layout())
                time.sleep(0.15)  # 增加睡眠时间减少CPU占用

            # 工作完成后显示最终状态
            console.print("\n[bold green]✅ 所有任务已完成![/bold green]")
            input("\n按回车键退出...")

        except SystemExit:
            console.print("\n[red]❌ 程序被用户中断[/red]")


if __name__ == "__main__":
    main()