__doc__="网站抓取进程"
__author__="Li Qingyun"
__date__="2025-03-09"

from time import sleep

from core.capture.interface.capture_thread import CaptureThread
from core.extension.const.extension_type import ExtensionType
from core.extension.interface.extension import Extension
from core.filter.connections_filter import ConnectionsFilter
from core.request.interface.request_thread import RequestThread
from core.sniffer.connection.connection_tracker_thread import ConnectionTrackerThread
from core.sniffer.scapy.scapy_thread import ScapyThread
from core.util.io.log_util import LogUtil
from core.util.io.path_util import PathUtil
from core.util.network.port_pool import PortPool
from core.util.string.time_util import TimeUtil
from core.util.string.url_util import UrlUtil


class WebsiteSingleTabCaptureThread(CaptureThread):
    """
    单标签网站抓取进程
        注: 单次抓取为一个原子操作, 不能中断, 所以不检测stop_event信号
    """

    def __init__(self,
                 task_name: str,
                 capture_name: str,
                 url: str,
                 output_main_dir: str,
                 extension_config:dict=None,
                 request_config: dict=None,
                 sniffer_scapy_config: dict=None,
                 sniffer_conn_tracker_config: dict=None
                 ):
        """

        :param task_name:                       任务名
        :param capture_name:                    抓取进程名
        :param url:                             url
        :param output_main_dir:                 输出主目录
        :param extension_config:                扩展配置
        :param request_config:                  请求配置
        :param sniffer_scapy_config:            scapy配置
        :param sniffer_conn_tracker_config:     ConnectionTracker配置
        """

        # 初始化配置
        super().__init__(
            task_name=task_name,
            capture_name=f"WebsiteCaptureThread-{capture_name}",
            extension_config=extension_config,
            request_config=request_config,
            sniffer_scapy_config=sniffer_scapy_config,
            sniffer_conn_tracker_config=sniffer_conn_tracker_config
        )

        # 配置
        self.url = url                                  # 本次抓取的url
        self.url_for_dir = UrlUtil.get_main_domain(url) # 仅保留https://后的主域名的url, 为目录设计(目录中不能含有 / ? 等特殊字符)
        self.output_main_dir = output_main_dir          # 输出文件的主目录

        # 进程内共享的参数
        self.__create_time_str = TimeUtil.now_time_str()    # 本次抓取进程的创建时间
        self.__pid_to_monitor = None                        # 需要监控的pid
        self.__pcap_path = None                             # pcap文件路径
        self.__connections = None                           # 连接列表

        # 进程实例
        self.extension = None                       # 扩展(一般是外部进程, 也可能是线程)
        self.request_thread = None                  # 请求线程
        self.sniffer_scapy_thread = None            # scapy线程
        self.sniffer_conn_tracker_thread = None     # ConnectionTracker线程

        # 进程传递出来信息
        self.extension_info = None          # 扩展加载后回传的信息(如代理端口, 代理PID等)
        self.request_thread_info = None     # 请求线程创建后回传的信息(如浏览器PID等)

        pass


    def run(self):
        # 进程启动入口
        self._start_capture()

    def stop(self):
        # 设置停止标志位
        super().stop()


    def __update_output_main_dir(self):
        """
        更新输出主目录
            主要是使用代理信息创建存储目录
        :return:
        """
        # 判断是否是代理
        if self.__is_extension_proxy() is True:
            # 获取配置中的协议栈
            protocol_stack = self.extension_config.get('protocol_stack')
            # 代理输出目录的格式
            # - output/google.com/proxy/[transport_protocol]/['security_protocol']/['transport_protoecol']/traffic.pacp
            # 例子: output/google.com/proxy/vless/tls/ws/2021-08-01-12-00-00/traffic.pcap
            self.output_main_dir = PathUtil.dir_path_join(
                self.output_main_dir,  # 输出主目录
                self.url_for_dir,                 # url
                self.extension_config.get('extension_type').value,   # 扩展类型
                protocol_stack.control.value,       # 控制协议
                protocol_stack.security.value,      # 安全协议
                protocol_stack.transport.value,     # 传输协议
                self.__create_time_str              # 任务创建时间
            )
        else:
            # 没有任何拓展(直连)的目录
            # - output/google.com/direct/2021-08-01-12-00-00/traffic.pcap
            self.output_main_dir = PathUtil.dir_path_join(
                self.output_main_dir,              # 输出主目录
                self.url_for_dir,                 # url
                'direct',                           # 类型
                self.__create_time_str              # 任务创建时间
            )


    def __is_extension_proxy(self):
        """
        判断扩展是否是代理
        :return:
        """
        if self.extension_config is None:
            return False
        return self.extension_config.get('extension_type') == ExtensionType.PROXY


    # 如果有别的拓展, 也可以在这写拓展方法
    # def __is_extension_tor(self):
    #     return self.extension_config.get('extension_type') == ExtensionType.TOR


    def __load_extension(self):
        """
        装载扩展
        :return:
        """
        if self.extension_config is None:
            LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 没有扩展需要装载")
            return

        # 如果是代理扩展, 需要获取一个端口
        if self.__is_extension_proxy():
            self.extension_config.update({
                'proxy_port': PortPool().get_port(),
                'log_file_dir': self.output_main_dir
            })

        # 创建扩展
        self.extension = Extension.create_extension_by_config(self.extension_config)
        # 装载扩展 (todo: 如果是thread类型的Extension, 需要包装, 没法用start启动)
        self.extension.load_extension()

        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 扩展正在装载, 等待3秒...")

        sleep(3)

        # 获取扩展信息(协议栈/主要是pid)
        self.extension_info = self.extension.get_extension_info()
        pass


    def __create_request_thread(self):
        """
        创建request线程
        :return:
        """
        if self.request_config is None:
            LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 没有 Request 线程需要创建")
            return

        # 如果使用的扩展是代理
        if self.__is_extension_proxy():
            self.request_config.update({
                'use_proxy': True,
                'proxy_port': self.extension_info.get('proxy_port')
            })

        # 把url等参数加入config中
        self.request_config.update({
            'url': self.url,
            'timeout': 0,
            'screenshot_dir': self.output_main_dir
        })

        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 正在创建 Request 线程")

        # 创建request线程
        self.request = RequestThread.create_request_thread_by_config(task_name=self.task_name,
                                                                     request_name=self.capture_name,
                                                                     config=self.request_config)
        # 创建request
        self.request.create_request()
        # 获取request线程信息
        self.request_info = self.request.get_request_thread_info()

        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] Request 线程信息: {self.request_info}")

        # 设置pid
        if self.__is_extension_proxy():
            self.pid_to_monitor = self.extension_info.get('pid')
        else:
            self.pid_to_monitor = self.request_info.get('pid')


    def __create_and_start_sniffer(self):
        """
        创建并启动流量嗅探模块(包括Scapy和ConnectionTracker)

        流程:
            1. 设置pcap路径
            2. 创建scapy线程, 但需要检查是否传入sniffer_scapy_config, 如果传入了应该特别处理
            3. 启动scapy线程
            4. 创建ConnectionTracker线程, 但需要检查是否传入sniffer_conn_tracker_config, 如果传入了应该特别处理
            5. 启动ConnectionTracker线程
        :return:
        """
        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 正在启动 Sniffer 模块 (Scapy)")

        # 1. 设置pcap路径
        self.__pcap_path = PathUtil.file_path_join(
            self.output_main_dir,
            file_path=f'{self.url_for_dir}_{self.__create_time_str}.pcap'
        )
        # 2. 创建scapy线程, 但需要检查是否传入scapy_config, 如果传入了应该特别处理

        # 2.1 如果没有Config,先创建一个
        if self.sniffer_scapy_config is None:
            self.sniffer_scapy_config = {}

        # 2.2 如果是代理且没有指定表达式, 需要把远程地址和端口生成一个过滤表达式传入scapy
        if self.__is_extension_proxy() and self.sniffer_scapy_config.get('filter_expr') is None:
            # 主动创建一个但是没有传入scapy_config
            remote_addr = self.extension_info.get('protocol_stack').remote_address
            remote_port = self.extension_info.get('protocol_stack').remote_port
            filter_expr = f"host {remote_addr} and port {remote_port}"
            self.sniffer_scapy_config.update({'filter_expr': filter_expr})

        # 2.3 如果配置中没有指定保存目录, 就把生成的pcap目录设置进去
        if self.sniffer_scapy_config.get('output_file_path') is None:
            self.sniffer_scapy_config.update({'output_file_path': self.__pcap_path})

        # 2.4 指定网卡
        if self.sniffer_scapy_config.get('network_interface') is None:
            self.sniffer_scapy_config.update({'network_interface': 'none'})

        # 2.3 根据 sniffer_config 创建
        self.sniffer_scapy_thread = ScapyThread.create_scapy_thread_by_config(task_name=self.task_name,
                                                                              config=self.sniffer_scapy_config)
        # end if

        # 3. 启动scapy线程
        self.sniffer_scapy_thread.start()

        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 正在启动 Sniffer 模块 (ConnectionTracker)")

        # 4. 检查是否传入conn_tracker_config
        if self.sniffer_conn_tracker_config is None:
            # 创建连接追踪线程
            self.sniffer_conn_tracker_thread = ConnectionTrackerThread(
                task_name=self.task_name,
                pid=self.pid_to_monitor,
                log_file_dir=self.output_main_dir,
                log_file_name=f'{self.url_for_dir}_{self.pid_to_monitor}_{self.__create_time_str}.log'
            )
        else:
            # todo: 如果传入了config, ConnectionTrackerThread
            # 创建连接追踪线程
            self.sniffer_conn_tracker_thread = ConnectionTrackerThread.create_connection_tracker_thread_by_config(task_name=self.task_name,
                                                                                                                  config=self.sniffer_conn_tracker_config)
        # end if
        # 5. 启动连接追踪
        self.sniffer_conn_tracker_thread.start()

    def __visit_website(self):
        """
        访问网站(启动request进程)
        :return:
        """
        if self.request is None:
            raise ValueError("[WebsiteCaptureThread] Request 线程不存在")

        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] Request 线程开始发送请求")

        # request进程启动
        self.request.start()
        # 阻塞等待request进程执行结束
        self.request.join()
        pass


    def __unload_extension(self):
        """
        卸载扩展
        :return:
        """
        if self.extension is None:
            LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 没有扩展需要卸载")
            return

        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 正在卸载扩展")

        # 如果是代理扩展, 需要释放一个端口
        if self.extension_info.get('proxy_port') is not None:
            PortPool().release_port(self.extension_info.get('proxy_port'))

        # 卸载扩展 (todo: 无法兼容thread类型的Extension)
        self.extension.unload_extension()


    def __stop_sniffer(self):
        """
        停止流量嗅探模块
        :return:
        """
        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 正在停止 Sniffer 模块")

        # 1. 停止scapy线程
        if self.sniffer_scapy_thread is not None:
            self.sniffer_scapy_thread.stop()
        # 2. 停止ConnectionTracker线程
        if self.sniffer_conn_tracker_thread is not None:
            self.sniffer_conn_tracker_thread.stop()

        pass


    def __filter_pcap(self):
        """
        根据ConnectionTracker跟踪的连接, 过滤pcap文件
            注: 如果是代理, 无需过滤
        :return:
        """
        # 如果扩展是代理则无需过滤
        if self.__is_extension_proxy() is True:
            LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 代理下无需过滤")
            return

        LogUtil().debug(self.task_name, f"[WebsiteCaptureThread] 正在过滤 pcap 文件")

        # scapy 嗅探信息(pcap路径和connection列表)
        pcap_path = self.sniffer_scapy_thread.output_file
        conns = self.sniffer_conn_tracker_thread.get_connections_list()  # 只取Connection对象列表, 不要原dict

        # 根据 scapy 抓的包与连接列表, 过滤pcap文件
        ConnectionsFilter.filter_pcap(pcap_path=pcap_path, connections_list=conns)
        pass


    def _start_capture(self):
        """
        运行抓取流程
        """
        # 0. 更新主输出目录
        self.__update_output_main_dir()

        # 1. 启动扩展(进程/线程)(非阻塞)
        self.__load_extension()

        # 2. 创建请求线程(非阻塞)
        self.__create_request_thread()

        # 3. 启动流量嗅探(非阻塞)
        self.__create_and_start_sniffer()

        # 4. 访问网站(阻塞)
        self.__visit_website()

        # 5. 卸载扩展
        self.__unload_extension()

        # 6. 关闭嗅探进程
        self.__stop_sniffer()

        # 7. 过滤pcap文件
        self.__filter_pcap()

        # todo: 8. 处理和识别流量

        # 9. 清理
        self.clear()

        pass



    def clear(self):
        """
        清理方法, 用于线程退出时执行
        :return:
        """
        # 没什么需要清理的, 空着就好
        pass



