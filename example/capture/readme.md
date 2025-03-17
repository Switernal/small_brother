# Capture 示例

## 1. 介绍

Capture 定义为单次抓取流程, 可以在不使用任务的情况下, 直接创建一个 CaptureThread 开启单次抓取流程

> 请注意: CaptureThread 是个抽象类不可实例化, 需要继承 CaptureThread 创建一个具体的子类再实例化

## 2. 使用示例

### 2.1 Website 网站类型

### 2.1.1 Single-Tab 单标签类型

> 实现类: `WebsiteSingleTabCaptureThread`

1. `task_name`: 理论上是上游 `TaskThread` 传入的, 如果只是为了测试抓取一次, 可以传入一个虚构的 `task_name`, 因为日志保存是按 Task 名来保存. 如果不传或者为 `None`, 容易造成日志混乱
2. `capture_name`: 抓取进程的进程名, 主要是日志中进程名会体现
3. `url`: 要访问的完整 URL
4. `output_main_dir`: 输出文件的主目录, 后面抓取的内容会在这个目录下创建子目录后存入
5. `extension_config`: 扩展配置
   1. 直连一般没有就传入 `None` 即可
   ```python
    extension_config = None
   ```
   2. 如果是代理, 可以传入代理配置信息
   ```python
   # 代理配置
    extension_config = {
        "extension_type": ExtensionType.PROXY,
        "proxy_type": ProxyType.MIHOMO,
        "protocol_stack": ProtocolStack(
            control=ControlProtocol.VLESS,
            security=SecurityProtocol.REALITY_VISION,
            transport=TransportProtocol.TCP,
            remote_address="10.0.0.1",
            remote_port=443
        ),
        'proxy_config': {
            'basic_config_dir': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/basic_configs'),
            'work_dir': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/basic_configs'),
            'node_config_dir': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/node_config'),
            'config_file_path': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/node_config/mihomo_config_vless_reality-xtls-rprx-vision_tcp.yaml'),
            'binary_file_path': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/binary_file/mihomo-verge_linux_x86_64')
        }
    }
   ```
6. `request_config`: 请求配置, 这里是浏览器单网页模式
    ```python
    request_config = {
        "request_type": RequestType.BROWSER_CHROME_SINGLE_TAB,
    }
    ```
7. `sniffer_scapy_config`: 流量嗅探配置, 这里是使用 scapy 进行嗅探. 
    1. 如果是直连, 可以不指定`filter_expr` . 甚至可以将 sniffer_scapy_config 这一项设为 None. 如果不指定网卡, 则会根据系统自动选择
    2. 如果是代理, `filter_expr` 参数可以传入指定的scapy过滤器表达式. 也可以不传, 会根据 `ProtocolStack` 的 `remote_address` 与 `remote_port` 自动生成
    3. mac 和 linux 的网卡不同, mac为`en0`, linux为`eth0`. 请根据实际情况修改 
    ```python
    # 嗅探配置指定网卡和过滤规则
    sniffer_scapy_config = {
        'network_interface': 'en0',
        'filter_expr': 'host 10.0.0.1 and port 443'
    }
    ```
8. `sniffer_conn_tracker_config`: 连接追踪配置(暂未实现). 未来可以通过参数传入指定的轮询间隔等
9. 创建请求线程
10. 使用 `.start()` 方法启动线程