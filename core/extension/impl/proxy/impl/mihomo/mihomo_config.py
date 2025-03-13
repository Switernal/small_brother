__doc__ = "Mihomo配置类"
__author__ = "Li Qingyun"
__date__ = "2025-02-28"

import os
import platform

from core.extension.impl.proxy.interface.proxy_config import ProxyConfig
from core.util.io.path_util import PathUtil
from core.util.multiprocessing.outer_subprocess_helper import OuterSubProcessHelper

# 当前目录
_CURRENT_PATH = os.path.dirname(__file__)

class MihomoProxyConfig(ProxyConfig):

    def __init__(self,
                 basic_config_dir: str = None,
                 work_dir: str = None,
                 node_config_dir: str = None,
                 config_file_path: str = None,
                 binary_file_path: str = None,
                 ):
        super().__init__(
            basic_config_dir=basic_config_dir,
            work_dir=work_dir,
            node_config_dir=node_config_dir,
            config_file_path=config_file_path,
        )
        self.binary_file_path = binary_file_path
        pass


    def get_binary_file_path(self):
        """二进制文件路径"""
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
        """代理基本配置路径"""
        if self.basic_config_dir:
            return self.basic_config_dir

        # 配置文件路径
        config_dir = PathUtil.dir_path_join(_CURRENT_PATH, 'basic_configs')
        return config_dir


    def get_node_config_dir(self):
        """代理节点配置路径"""
        if self.node_config_dir:
            return self.node_config_dir

        # 配置文件路径
        config_dir = PathUtil.dir_path_join(_CURRENT_PATH, 'node_config')
        return config_dir


    def _get_config_file_name(self, protocol_stack):
        """获取配置文件名"""
        # 配置文件名前缀
        config_file_prefix = 'mihomo_config_'
        # 配置文件名后缀
        config_file_suffix = '.yaml'
        # 根据协议栈生成所需要的配置文件名字, 格式: 前缀_协议栈_后缀
        return f'{config_file_prefix}{protocol_stack}{config_file_suffix}'


    def get_node_config_file_path(self, protocol_stack):
        """获取配置文件路径"""
        # 如果传入了, 就用传入的; 没有就用默认的
        if self.config_file_path:
            return self.config_file_path

        return PathUtil.file_path_join(
            self.get_node_config_dir(),
            file_path=self._get_config_file_name(protocol_stack))
        pass


    def get_work_dir(self):
        """工作目录"""
        if self.work_dir:
            return self.work_dir
        work_dir = PathUtil.dir_path_join(_CURRENT_PATH, 'basic_configs')
        return work_dir


    @staticmethod
    def from_dict(config_dict):
        """
        从配置字段创建
        :return:
        """
        return MihomoProxyConfig(
            basic_config_dir=config_dict.get('basic_config_dir'),
            work_dir=config_dict.get('work_dir'),
            node_config_dir=config_dict.get('node_config_dir'),
            config_file_path=config_dict.get('config_file_path'),
            binary_file_path=config_dict.get('binary_file_path'),
        )

    def to_dict(self):
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




