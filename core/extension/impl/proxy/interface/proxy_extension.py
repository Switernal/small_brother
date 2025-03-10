__doc__ = '代理类'
__auther__ = 'Li Qingyun'
__date__ = '2025-02-24'

from abc import abstractmethod, ABCMeta

from core.extension.const.extension_type import ExtensionType
from core.extension.impl.proxy.const.protocol_stack import ProtocolStack
from core.extension.impl.proxy.const.proxy_type import ProxyType
from core.extension.impl.proxy.interface.proxy_config import ProxyConfig
from core.extension.interface.extension import ExtensionSubProcess
from core.util.io.path_util import PathUtil
from core.util.multiprocessing.outer_subprocess_helper import OuterSubProcessHelper


class ProxyExtension(ExtensionSubProcess, metaclass=ABCMeta):
    """
    代理类接口, 所有其他代理必须从这个类继承并实现对应的方法
    """

    def __init__(self,
                 proxy_type: ProxyType,
                 proxy_port: int,
                 protocol_stack: ProtocolStack,
                 proxy_config: ProxyConfig,
                 log_file_dir: str,
                 enable_log: bool = True
                 ):
        """
        初始化
        :param proxy_type:      代理类型
        :param proxy_port:            端口
        :param protocol_stack:  协议栈
        :param proxy_config:          配置实例
        :param log_file_dir:    日志文件目录
        :param enable_log:      是否开启日志(默认开启)
        """
        # 配置文件路径
        self.proxy_type = proxy_type          # 代理类型
        self.proxy_config = proxy_config                  # 配置实例
        self.log_file_dir = log_file_dir
        self.proxy_port = proxy_port                      # 端口
        self.protocol_stack = protocol_stack  # 协议栈

        # 注意: 由于ExtensionSubProcess还继承了Extension类, 调用父类初始方法必须用"类名.__init__()"
        super().__init__(
            name=f'{self.proxy_type}_{protocol_stack}',
            start_command=self.start_command,
            enable_log=enable_log,
            log_file_path=PathUtil.file_path_join(
                self.log_file_dir,
                file_path=f'{self.proxy_type.value}_{protocol_stack}.log'
            ),
        )

        # 检查是否传入参数错误
        self._set_port_and_protocol_stack()

        pass

    @property
    @abstractmethod
    def start_command(self):
        """启动命令"""
        return ''
        pass


    def _set_port_and_protocol_stack(self):
        """检查端口和协议栈是否有误"""
        # 端口检查
        if self.proxy_port < 0 or self.proxy_port > 65535:
            raise ValueError("端口范围错误")

        # 协议栈检查
        if self.protocol_stack.validation_check() is False:
            raise ValueError("传入的协议栈有误")


    def get_extension_info(self):
        """
        获取扩展信息
        :return: 扩展信息
        """
        return {
            'extension_type': ExtensionType.PROXY,
            'proxy_type': self.proxy_type,
            'pid': self.pid,
            'proxy_port': self.proxy_port,
            'protocol_stack': self.protocol_stack,
        }
    @abstractmethod
    def to_dict(self):
        pass

    @staticmethod
    @abstractmethod
    def from_dict(config_dict):
        pass


    @staticmethod
    def create_extension_by_config(proxy_extension_config: dict):
        """
        根据配置创建一个代理扩展
        :param proxy_extension_config:
        :return:
        """
        if proxy_extension_config.get('extension_type') is None \
            or proxy_extension_config.get('extension_type') is not ExtensionType.PROXY:
            raise ValueError(f"[ProxyExtension] 传入的配置不是代理配置")

        if proxy_extension_config.get('proxy_type') == ProxyType.MIHOMO:
            from core.extension.impl.proxy.impl.mihomo.mihomo_proxy_extension import MihomoProxyExtension
            return MihomoProxyExtension.from_dict(proxy_extension_config)

        elif proxy_extension_config.get('proxy_type') == ProxyType.V2RAY:
            raise ValueError(f"[ProxyExtension] 暂不支持创建{ProxyType.V2RAY.value}代理")

        elif proxy_extension_config.get('proxy_type') == ProxyType.XRAY:
            raise ValueError(f"[ProxyExtension] 暂不支持创建{ProxyType.XRAY.value}代理")
        else:
            raise ValueError("[ProxyExtension] 不支持的代理类型")