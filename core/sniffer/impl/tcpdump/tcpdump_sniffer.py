__doc__ = "tcpdump 嗅探器"
__author__ = "Li Qingyun"
__date__ = "2025-12-03"

from core.sniffer.impl.tcpdump.tcpdump_util import TcpdumpUtil
from core.sniffer.interface.traffic_sniffer import TrafficSniffer
from core.util.multiprocessing import OuterSubProcessHelper

class TcpdumpSniffer(TrafficSniffer):
    """
    tcpdump 子进程工具类手机号
    """
    def __init__(self,
                 task_name: str,
                 output_file_path: str,
                 network_interface: str = None,
                 params: dict = None
                 ):
        """

        :param task_name:           任务名称
        :param output_file_path:    输出文件路径
        :param network_interface:   网络接口
        :param params:              指令参数
        """

        # 1. 初始化父类
        self.task_name = task_name
        self.output_file_path = output_file_path
        self.network_interface = network_interface
        self.params = params

        super().__init__(
            task_name=task_name,
            output_file_path=output_file_path,
            network_interface=network_interface,
            params=params
        )

        # 2. tcpdump 指令位置
        self.tcpdump_cmd = TcpdumpUtil.get_tcpdump_cmd()

        # 3. 生成过滤表达式
        self.generate_filter_expr_by_params()

        # 4. 生成启动指令
        self.generate_startup_instruction()

        # 5. 创建子进程工具类, 准备就绪
        self.tcpdump_subprocess = OuterSubProcessHelper(
            name="tcpdump子进程",
            start_command=self.startup_instruction,
            logger_name=self.task_name,
        )
        pass

    def generate_startup_instruction(self):
        """
        生成启动指令
        """
        self.startup_instruction = self.tcpdump_cmd + [
            '-i', self.network_interface,     # 网络接口
            '-w', self.output_file_path,      # 输出文件路径
            '-f', self.filter_expr,           # 过滤表达式
            # '-n',                           # 不进行DNS解析
            '-B', '51200',                    # 缓冲区大小, 单位KB
        ]
        pass


    def start_sniffer(self):
        """
        启动抓包
        """
        self.tcpdump_subprocess.start_process()
        pass

    def stop_sniffer(self):
        """
        停止抓包
        """
        self.tcpdump_subprocess.stop_process()
        pass

    @staticmethod
    def creat_sniffer_by_config(task_name, config: dict):
        return TcpdumpSniffer(
            task_name=task_name,
            output_file_path=config.get('output_file_path'),
            network_interface=config.get('network_interface'),
            params=config.get('params'),
        )
        pass

    def handle_log(self):
        pass