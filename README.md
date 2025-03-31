# small_brother

# 这是什么

- 支持自定义且和扩展的流量捕捉工具


# 这能做什么

- 自定义抓取流量的流程

- 自定义抓取流量的扩展

- 自定义抓取流量的过滤方式

- 助你成为老小哥

# 使用说明

## 1. 环境配置

### 1.1 依赖包

按 requirements.txt 中的指示安装依赖. Python 版本大于等于 3.9 即可.

推荐使用 Anaconda.

### 1.2 Selenium 设置

如欲启动浏览器抓取网站流量, Windows 和 Mac 用户请先安装 Chrome.

linux 用户请先安装 Chrome, 并下载对应版本的 ChromeDriver. 
然后将 ChromeDriver 压缩包解压后, 将 `chromedriver-linux64` 放入 `/usr/bin` 目录中

Chrome 及 ChromeDriver 下载地址: https://googlechromelabs.github.io/chrome-for-testing/#stable

## 2. 使用示例

可在 example 目录下寻获示例代码

示例说明:

- capture/website/website_single_tab_capture_example.py: 仅抓取单个网站一次

- task/website/website_single_tab_task_example.py: 执行单个任务

- task_manager/task_manager_example.py: 多线程并发执行多个任务

## 3. 其他

如有其他问题, 可在 issue 中提出, 或亲临实验室