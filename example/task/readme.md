# Task 示例

## 1. 介绍

Task 定义: 指定一组特定配置组合, 然后在一个指定的抓取目标列表内重复指定次数的流量抓取操作

可以在不使用任务管理器 `TaskManager` 的情况下, 直接创建一个 `TaskThread` 开启单次抓取流程

> 请注意: `TaskThread` 是个抽象类不可实例化, 需要继承 `TaskThread` 创建一个具体的子类再实例化

Task 举例: 

- 指定以下配置的抓取自动化流程为一个任务:

  - 扩展: 一个协议为 vless+tls+ws 的特定节点, 代理类型为 mihomo 的代理客户端
  - 请求类型: 一个浏览器单标签请求
  - 嗅探设置: 指定网卡为`en0`和 `filter_expr`为代理节点ip和端口的过滤规则
  - 网站列表: Chrome 热门 1000 网站列表
  - 抓取策略: 每个网站抓取 5 次

当然, 你可以随意组合其中的配置, 但每一组配置为一个 Task

但你不能在一个 task 中出现多个同类配置, 比如指定了两个代理节点, 或是同时抓取代理和直连的流量, 这是不允许的. 你也不可以在一个任务中指定两种抓取方式, 比如同时抓取单标签页和多标签页

如果你有上述的需求, 你可以通过为每一个节点创建一个 Task, 然后使用 `TaskManager` 来实现多任务并发/并行


## 2. 使用示例

### 2.1 Website 网站类型

### 2.1.1 Single-Tab 单标签类型

> 实现类: `WebsiteSingleTabTaskThread`

执行步骤: 

1. 指定任务配置文件的绝对路径
```python
task_description_path = 'example/task/website/task_description_example/TaskDescription-test_task_direct.yaml'
```

2. 从配置文件创建一个 `WebsiteSingleTabTaskThread` 实例
```python
task_thread = WebsiteSingleTabTaskThread.create_task_from_config_file(task_config_file_path=task_description_path)
```

3. 启动任务线程
```python
task_thread.start()
```