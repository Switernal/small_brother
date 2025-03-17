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
    """
    代理扩展类-Mihomo 代理
        本质上是一个子进程助理类, 用于创建和控制外部子进程

        继承关系: MihomoProxyExtension -> ProxyExtension -> ExtensionSubProcess -> OuterSubProcessHelper
    """

    def __init__(self,
                 protocol_stack: ProtocolStack,
                 proxy_port: int,
                 log_file_dir: str,
                 enable_log: True,
                 proxy_config: MihomoProxyConfig = MihomoProxyConfig()
                 ):
        """

        :param protocol_stack:  协议栈对象
        :param proxy_port:      本地代理端口(本地混合代理(socks5+http)端口)
        :param log_file_dir:    mihomo控制台输出的日志文件目录
        :param proxy_config:    代理配置对象
        :param enable_log:      是否开启日志(默认开启)
        """
        super().__init__(
            proxy_type=ProxyType.MIHOMO,
            protocol_stack=protocol_stack,
            proxy_port=proxy_port,
            proxy_config=proxy_config,
            log_file_dir=log_file_dir,
            enable_log=enable_log
        )


    @property
    def start_command(self):
        """
        设置启动命令
        :return:
        """
        return [
            # 'exec',
            self.proxy_config.get_binary_file_path(),  # 二进制文件路径
            '-d', self.proxy_config.get_work_dir(),  # 配置 CLASH_HOME_DIR, 即 configuration directory
            '-f', self.proxy_config.get_node_config_file_path(self.protocol_stack)  # 指定 CLASH_CONFIG_FILE, 即指定的配置文件 specified configuration file
        ]

    def load_extension(self):
        """
        加载扩展
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
        参数示例:
        {
            'extension_type': ExtensionType.PROXY,
            'protocol_stack': ProtocolStack 对象实例 (非dict)
            'proxy_port': 7897
            'enable_log': true,
            'log_file_dir': '/tmp/output'
            'proxy_config':
               'basic_config_dir': 'proxy/mihomo/basic_configs'
               'work_dir': 'proxy/mihomo/basic_configs'
               'node_config_dir': 'proxy/mihomo/node_config'
               'config_file_path': 'proxy/mihomo/node_config/mihomo_config_vless_reality-xtls-rprx-vision_tcp.yaml'
               'binary_file_path': 'proxy/mihomo/binary_file/mihomo-verge_linux_x86_64'
        }

        特别注意:
            这里传入的 extension_config 是 TaskExtensionConfig 对原始配置解析过后
            在 CaptureThread 重新封装的, 不是原始yaml文件中的 extension_config
            因此:
                1. 'extension_type' 是一个 ExtensionType 类的枚举对象, 而不是字符串
                2. 'protocol_stack'字段 是一个 ProtocolStack 对象实例, 而不是 dict
                3. 'proxy_config' 字段仍是原始 dict, 需转成对象再传入构造方法 (Task层不需要用这个字段, 所以没有解析)

        为什么会这么设计:
            因为 Task 层面需要对 Extension 进行判断, 根据不同类型分流到不同扩展类处理
            另外若 Extension 是代理, 则需要进行额外设置, 因此需要提前解析
            既然 Task 已经解析了部分字段, 那么就干脆重构一个 extension_config 字典给 ProxyExtension 层用
            所以会出现部分字段已经变成对象的情况
            反之, to_dict() 方法在向上返回 dict 时, 对应字段也应为对象, 而非字符串或原始dict
            请多加注意

        :return: MihomoProxyExtension 对象实例
        """
        proxy_config = extension_config.get('proxy_config')

        # 如果未指定是否开启日志, 默认开启
        enable_log = True
        if extension_config.get('enable_log'):
            enable_log = extension_config.get('enable_log')

        return MihomoProxyExtension(
            protocol_stack=extension_config.get('protocol_stack'),
            proxy_port=extension_config.get('proxy_port'),
            enable_log=enable_log,
            log_file_dir=extension_config.get('log_file_dir'),
            proxy_config=MihomoProxyConfig.from_dict(proxy_config), # 转换成对象再传入
        )

    def to_dict(self):
        """
        将对象转换为字典
            注意:
                'extension_type' 和 'protocol_stack' 字段为对象实例
                'proxy_config' 为字典
        :return:
        """
        return {
            'extension_type': ExtensionType.PROXY,      # ExtensionType 类的枚举对象, 非字符串
            'protocol_stack': self.protocol_stack,      # ProtocolStack 对象实例, 非 dict
            'proxy_port': self.proxy_port,
            'log_file_dir': self.log_file_dir,
            'proxy_config': self.proxy_config.to_dict() # 需要对象转换为字典, 因为task层面不需要这个字段
        }