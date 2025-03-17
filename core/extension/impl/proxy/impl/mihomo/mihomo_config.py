__doc__ = "Mihomo配置类"
__author__ = "Li Qingyun"
__date__ = "2025-02-28"

import os
import platform

from core.extension.impl.proxy.const.protocol_stack import ProtocolStack
from core.extension.impl.proxy.interface.proxy_config import ProxyConfig
from core.util.io.path_util import PathUtil
from core.util.multiprocessing.outer_subprocess_helper import OuterSubProcessHelper

# 当前目录
_CURRENT_PATH = os.path.dirname(__file__)

class MihomoProxyConfig(ProxyConfig):
    """
    Mihomo 配置类
        继承关系: MihomoProxyConfig -> ProxyConfig
    """

    def __init__(self,
                 basic_config_dir: str = None,
                 work_dir: str = None,
                 node_config_dir: str = None,
                 config_file_path: str = None,
                 binary_file_path: str = None,
                 ):
        """
        构造函数

            必要代表必须传入, 建议代表可以为空但最好传一个

        :param basic_config_dir: (必要)    基础配置文件目录
        :param work_dir:         (非必要)  工作目录(通常和 basic_config_dir 一样, 可以不传; 传入代表特别指定)
        :param node_config_dir:  (建议)    节点配置文件目录(也可以和 basic_config_dir 一样, 但不推荐)
        :param config_file_path: (一般建议) 节点配置文件路径(如果未传入, 就从node_config_dir下根据协议栈生成规则寻找)
        :param binary_file_path: (必要)    二进制可执行文件路径(如果未传入, 就用core中默认的, 根据系统选择)
        """
        super().__init__(
            basic_config_dir=basic_config_dir,
            work_dir=work_dir,
            node_config_dir=node_config_dir,
            config_file_path=config_file_path,
        )
        self.binary_file_path = binary_file_path
        pass


    def get_binary_file_path(self):
        """
        获取二进制文件路径
        :return:
        """
        if self.binary_file_path:
            return self.binary_file_path

        binary_file_name = ''
        # 二进制文件名, 根据系统判断使用哪个
        if platform.system() == "Linux":        # Linux内核, 从deb提取的
            binary_file_name = 'mihomo-verge_linux_x86_64'
        elif platform.system() == "Darwin":     # macOS
            binary_file_name = 'mihomo-verge_darwin_arm64'
        elif platform.system() == "Windows":
            # _EXECUTABLE_FILE = 'mihomo-verge_windows_x86_64.exe'
            raise ValueError(f"暂不支持 Windows")
        else:
            raise ValueError(f"不支持的系统: {platform.system()}")
        # 二进制文件路径
        binary_file_path = PathUtil.file_path_join(_CURRENT_PATH, 'binary_file', file_path=binary_file_name)
        # 提权一下
        OuterSubProcessHelper.quick_execute_cmd(f'chmod 755 {binary_file_path}')

        return binary_file_path


    def get_basic_config_dir(self):
        """
        获取代理基本配置路径
        :return:
        """
        if self.basic_config_dir:
            return self.basic_config_dir

        # 默认的配置文件路径
        config_dir = PathUtil.dir_path_join(_CURRENT_PATH, 'basic_configs')
        return config_dir


    def get_node_config_dir(self) -> str:
        """
        获取代理节点配置路径
            如果特别指定了, 就用指定的 (建议指定)
            如果没指定, 就和 basic_config_dir 一样

        :return: 配置文件路径
        """
        if self.node_config_dir:
            return self.node_config_dir

        if self.basic_config_dir:
            return self.basic_config_dir

        # 默认的配置文件路径
        config_dir = PathUtil.dir_path_join(_CURRENT_PATH, 'node_config')
        return config_dir


    def _get_config_file_name(self, protocol_stack: ProtocolStack) -> str:
        """
        获取节点配置文件名(根据协议栈生成)

        :param protocol_stack: 协议栈对象
        :return:
        """
        # 配置文件名前缀
        config_file_prefix = 'mihomo_config_'
        # 配置文件名后缀
        config_file_suffix = '.yaml'
        # 根据协议栈生成所需要的配置文件名字, 格式: 前缀_协议栈_后缀
        return f'{config_file_prefix}{protocol_stack}{config_file_suffix}'


    def get_node_config_file_path(self, protocol_stack):
        """
        获取节点配置文件路径(根据协议栈对象)
        :param protocol_stack: 协议栈对象
        :return:
        """
        # 如果指定了配置文件路径, 就用传入的
        if self.config_file_path:
            return self.config_file_path

        # 如果未指定配置文件, 就从节点配置目录下, 根据协议栈生成规则寻找
        return PathUtil.file_path_join(
            self.get_node_config_dir(),
            file_path=self._get_config_file_name(protocol_stack))
        pass


    def get_work_dir(self):
        """
        mihomo 工作目录
            一般和 basic_config_dir 一样, 可以不传
            如果特别指定了, 就用指定的
        :return:
        """
        if self.work_dir:
            return self.work_dir
        if self.basic_config_dir:
            return self.basic_config_dir

        work_dir = PathUtil.dir_path_join(_CURRENT_PATH, 'basic_configs')
        return work_dir


    @staticmethod
    def from_dict(config_dict: dict) -> 'MihomoProxyConfig':
        """
        从配置字段创建

        :param config_dict: 配置字典
            参数示例:
            {
                'basic_config_dir': '/user/luber/mihomo/basic_configs',
                'work_dir': '/user/luber/mihomo/basic_configs',
                'node_config_dir': '/user/luber/mihomo/node_config',
                'config_file_path': '/user/luber/mihomo/node_config/mihomo_config_vless_tls_ws.yaml',
                'binary_file_path': '/user/luber/mihomo/binary_file/mihomo-verge_linux_x86_64'
            }
        :return:
        """
        return MihomoProxyConfig(
            basic_config_dir=config_dict.get('basic_config_dir'),
            work_dir=config_dict.get('work_dir'),
            node_config_dir=config_dict.get('node_config_dir'),
            config_file_path=config_dict.get('config_file_path'),
            binary_file_path=config_dict.get('binary_file_path'),
        )

    def to_dict(self) -> dict:
        """
        转换为字典
        :return:
        """
        return {
            'basic_config_dir': self.basic_config_dir,
            'work_dir': self.work_dir,
            'node_config_dir': self.node_config_dir,
            'config_file_path': self.config_file_path,
            'binary_file_path': self.binary_file_path,
        }




