__doc__="Rich 列统计"
__author__="Li Qingyun"
__date__="2025-11-20"

from rich.progress import ProgressColumn
from rich.text import Text


class RichCountColumn(ProgressColumn):
    """自定义列，显示完成次数/总次数"""

    def render(self, task) -> Text:
        """渲染次数显示：已完成/总数"""
        if task.total and task.total > 0:
            return Text(f"{int(task.completed)}/{int(task.total)}", style="progress.percentage")
        return Text("?")