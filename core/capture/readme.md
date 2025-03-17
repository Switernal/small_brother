# Capture 模块

## 1. 模块说明

功能: 流量抓取流程, 执行一次 Capture 即为"完整的一次抓取流程"

> "完整的抓取流程"解释: 启动→加载扩展→创建请求进程→启动流量嗅探→发起请求→结束请求→结束流量嗅探→卸载扩展→结束

## 2. 模块结构

```shell
├── impl
│ └── website
│   └── website_single_tab_capture_thread.py
├── interface
│   └── capture_thread.py
└── readme.md
```

## 3. 模块详细说明

### 3.1 interface

Capture 的接口

#### 3.1.1 capture_thread.py

创建 CaptureThread 类, 继承自 BetterThread 类

```python
class CaptureThread(BetterThread):
```

功能: 定义了 Capture 线程应具备基础功能接口, 后续不同的任务可以从该类继承并进行扩展, 比如"网站抓取流程"、"APP抓取流程"等

### 3.2 impl

CaptureThread 的具体实现类

#### 3.2.1 website

针对网站的抓取流程实现模块

目前实现进度: 

[ √ ] WebsiteSingleTabCaptureThread: 单标签网站抓取流程

[ - ] WebsiteMultiTabCaptureThread 多标签网站抓取流程

##### 3.2.1.1 website_single_tab_capture_thread.py

功能: 单标签网站抓取流程

创建 WebsiteSingleTabCaptureThread 类, 继承自 CaptureThread 类

```python
class WebsiteSingleTabCaptureThread(CaptureThread):
```

