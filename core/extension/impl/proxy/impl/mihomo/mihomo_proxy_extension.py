__doc__='mihomo类(继承自ProxyExtension)'
__author__='Li Qingyun'
__date__='2025-03-03'

import yaml

from core.extension.const.extension_type import ExtensionType
from core.extension.impl.proxy.const.protocol_stack import ProtocolStack
from core.extension.impl.proxy.const.proxy_type import ProxyType
from core.extension.impl.proxy.impl.mihomo.mihomo_config import MihomoProxyConfig
from core.extension.impl.proxy.interface.proxy_extension import ProxyExtension
from core.util.io.log_util import LogUtil
from core.util.io.yaml_util import YamlUtil


class MihomoProxyExtension(ProxyExtension):
    """mihomo代理的管理类"""

    def __init__(self,
                 protocol_stack: ProtocolStack,
                 proxy_port: int,
                 log_file_dir: str,
                 proxy_config: MihomoProxyConfig = MihomoProxyConfig()
                 ):
        super().__init__(
            proxy_type=ProxyType.MIHOMO,
            protocol_stack=protocol_stack,
            proxy_port=proxy_port,
            proxy_config=proxy_config,
            log_file_dir=log_file_dir
        )


    @property
    def start_command(self):
        """设置启动命令"""
        return [
            # 'exec',
            self.proxy_config.get_binary_file_path(),  # 二进制文件路径
            '-d', self.proxy_config.get_work_dir(),  # 配置 CLASH_HOME_DIR, 即 configuration directory
            '-f', self.proxy_config.get_node_config_file_path(self.protocol_stack)  # 指定 CLASH_CONFIG_FILE, 即指定的配置文件 specified configuration file
        ]

    def load_extension(self):
        """
        载入扩展
        :return:
        """
        self.start_process()
        pass

    def unload_extension(self):
        """
        卸载扩展
        :return:
        """
        self.stop_process()
        pass


    def _set_port_and_protocol_stack(self):
        """
        设置端口和协议栈
        :return:
        """
        super()._set_port_and_protocol_stack()

        config_file_path = self.proxy_config.get_node_config_file_path(self.protocol_stack)

        # 修改yaml配置文件中的mixed-port值, 即代理监听端口

        config = YamlUtil().load(config_file_path)
        config['mixed-port'] = self.proxy_port
        YamlUtil().dump(config, config_file_path)

        LogUtil().debug('main', '[MihomoProxyExtension] Mihomo 配置成功')
        LogUtil().debug('main', f'\t使用的协议栈: {self.protocol_stack}')
        LogUtil().debug('main', f'\t使用的端口: {self.proxy_port}')
        LogUtil().debug('main', f'\t工作路径: {self.proxy_config.get_work_dir()}')
        LogUtil().debug('main', f'\t配置文件名: {config_file_path.split("/")[-1]}')
        pass


    def handle_log(self):
        """
        处理日志
        :return:
        """
        pass


    @staticmethod
    def from_dict(extension_config):
        """
        根据 Extension 配置创建对象
        :param extension_config:
        :return:
        """
        proxy_config = extension_config.get('proxy_config')
        return MihomoProxyExtension(
            protocol_stack=extension_config.get('protocol_stack'),
            proxy_port=extension_config.get('proxy_port'),
            log_file_dir=extension_config.get('log_file_dir'),
            proxy_config=MihomoProxyConfig.from_dict(proxy_config),
        )

    def to_dict(self):
        """
        将对象转换为字典
        :return:
        """
        return {
            'extension_type': ExtensionType.PROXY,
            'protocol_stack': self.protocol_stack,
            'proxy_port': self.proxy_port,
            'log_file_dir': self.log_file_dir,
            'proxy_config': self.proxy_config.to_dict()
        }