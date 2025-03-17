# Task 示例

## 1. 介绍

`TaskManager` 用于管理一组任务的执行, 当你有多个任务需要执行时, 可以使用任务组来管理, 而无需逐个手动执行

> 请注意: `TaskManager` 并不是个线程类, 在主进程中执行, 负责管理其他任务线程的创建和执行

## 2. 使用示例

使用时, 需要编写一个 task_group 描述文件, 将你的任务描述文件列表加入其中, 然后使用 `TaskManager` 来执行

执行步骤: 

1. 指定任务组配置文件的绝对路径
```python
task_group_file_path = 'example/task_manager/task_group_example.yaml'
```

2. 创建任务管理器实例
```python
task_manager = TaskManager(task_group_file_path=task_group_file_path)
```

3. 启动任务管理器
```python
task_manager.start_performing()
```