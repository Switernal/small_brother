__doc__ = "网站单标签单次抓取流程示例"
__author__ = "Li Qingyun"
__date__ = "2025-03-17"

import os
import sys
sys.path.append(os.getcwd())

from core.capture.impl.website.website_single_tab_capture_thread import WebsiteSingleTabCaptureThread
from core.extension import ExtensionType, ProxyType, ProtocolStack
from core.extension.impl.proxy.const.protocol_stack import ControlProtocol, SecurityProtocol, TransportProtocol
from core.request.const.request_type import RequestType
from core.util import PathUtil
from core.util.io.log_util import LogUtil

# 项目根路径(建议使用在操作系统中的绝对路径)
__project_root_dir = '/Users/your_user_name/PycharmProjects/small_brother'


def __capture_once_directly():
    """
    执行单次单网页访问流程 (直连)
    :return:
    """
    print('开始执行单次单网页访问流程(直连)')
    # 1. task_name 可以为 None, 但是如果开启了日志, 最好传入一个虚构的 task_name
    task_name = 'CaptureTest_Direct'
    # 2. 抓取进程的进程名
    capture_name = 'TestWebsiteSingleTabCaptureThread_Direct'
    # 3. 要访问的 URL
    url = "https://apple.cn/"
    # 4. 输出文件的主目录
    output_main_dir = PathUtil.dir_path_join(__project_root_dir, "example/capture/website/output/website_single_tab_capture_example/direct")
    # 5. 直连没有Extension
    extension_config = None
    # 6. 请求类型为浏览器单网页模式
    request_config = {
        "request_type": RequestType.BROWSER_CHROME_SINGLE_TAB,
    }
    # 7. 嗅探配置指定网卡和过滤规则
    sniffer_scapy_config = {
        'network_interface': 'en0',
    }
    # 8. todo: 该项配置暂时没有写对应的解析, 仅留作接口, 可传入但无任何效果
    # sniffer_conn_tracker_config = {
    #     'query_interval': 0.5
    # }
    # 9. 创建请求线程
    capture_thread = WebsiteSingleTabCaptureThread(
        task_name=task_name,
        capture_name=capture_name,
        url=url,
        output_main_dir=output_main_dir,
        extension_config=extension_config,
        request_config=request_config,
        sniffer_config=sniffer_scapy_config,
        # sniffer_conn_tracker_config=sniffer_conn_tracker_config
    )
    # 10. 启动线程
    capture_thread.start()
    capture_thread.join()       # 阻塞执行


def __capture_once_by_proxy():
    """
    执行单次单网页访问流程 (代理)
    :return:
    """
    print('开始执行单次单网页访问流程(代理)')
    # 1. task_name 可以为 None, 但是如果开启了日志, 最好传入一个虚构的 task_name
    task_name = 'CaptureTest_Proxy'
    # 2. 抓取进程的进程名
    capture_name = 'TestWebsiteSingleTabCaptureThread_Proxy'
    # 3. 要访问的 URL
    url = "https://apple.cn/"
    # 4. 输出文件的主目录
    output_main_dir = PathUtil.dir_path_join(__project_root_dir, "example/capture/website/output/website_single_tab_capture_example/proxy")
    # 5. 代理配置
    extension_config = {
        "extension_type": ExtensionType.PROXY,
        "proxy_type": ProxyType.MIHOMO,
        "protocol_stack": ProtocolStack(
            control=ControlProtocol.VLESS,
            security=SecurityProtocol.REALITY_VISION,
            transport=TransportProtocol.TCP,
            remote_address="23.106.154.40",
            remote_port=59932
        ),
        'proxy_config': {
            'basic_config_dir': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/basic_configs'),
            'work_dir': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/basic_configs'),
            'node_config_dir': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/node_config'),
            'config_file_path': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/node_config/mihomo_config_vless_reality-xtls-rprx-vision_tcp.yaml'),
            'binary_file_path': PathUtil.dir_path_join(__project_root_dir, 'personalized/extension/proxy/mihomo/binary_file/mihomo-verge_darwin_arm64')
        }
    }
    # 6. 请求类型为浏览器单网页模式
    request_config = {
        "request_type": RequestType.BROWSER_CHROME_SINGLE_TAB,
    }
    # 7. 嗅探配置指定网卡和过滤规则, 由于是代理, 只需要指定远程节点的ip和port就行
    sniffer_scapy_config = {
        'network_interface': 'en0',
        'filter_expr': 'host 23.106.154.40 and port 59932'
    }
    # 8. todo: 该项配置暂时没有写对应的解析, 仅留作接口, 可传入但无任何效果
    # sniffer_conn_tracker_config = {
    #     'query_interval': 0.5
    # }
    # 9. 创建请求线程
    capture_thread = WebsiteSingleTabCaptureThread(
        task_name=task_name,
        capture_name=capture_name,
        url=url,
        output_main_dir=output_main_dir,
        extension_config=extension_config,
        request_config=request_config,
        sniffer_config=sniffer_scapy_config,
        # sniffer_conn_tracker_config=sniffer_conn_tracker_config
    )
    # 10. 启动线程
    capture_thread.start()
    capture_thread.join()   # 阻塞执行


if __name__ == '__main__':
    # 设置日志
    LogUtil().enable_log = True     # 是否启用日志
    LogUtil().set_log_dir(PathUtil.dir_path_join(__project_root_dir, 'example/capture/website/output/log'))    # 日志目录

    # 直连
    __capture_once_directly()

    # 代理
    __capture_once_by_proxy()
