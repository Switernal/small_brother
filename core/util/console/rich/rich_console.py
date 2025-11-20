__doc__="Rich 统一终端对象"
__author__="Li Qingyun"
__date__="2025-11-20"

"""
来源: https://rich.pythonlang.cn/en/stable/console.html

为了完全控制终端格式，Rich 提供了一个 Console 类。
大多数应用程序只需要一个 Console 实例，因此您可能希望在模块级别或作为顶级对象的属性创建一个。
例如，您可以在项目中添加一个名为“console.py”的文件

然后，您可以像这样从项目中的任何地方导入控制台
```python
from my_project.console import console
````
控制台对象负责生成 ANSI 转义序列以进行颜色和样式处理。它会自动检测终端的功能，并在必要时转换颜色。
"""
from rich.console import Console
console = Console()