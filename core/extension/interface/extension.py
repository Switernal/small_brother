__doc__="Extension 抽象类"
__author__="Li Qingyun"
__date__="2025-03-09"

from abc import abstractmethod, ABCMeta

from core.extension.const.extension_type import ExtensionType
from core.util.multiprocessing.outer_subprocess_helper import OuterSubProcessHelper
from core.util.multithreading.better_thread import BetterThread


class Extension(metaclass=ABCMeta):
    """
    Extension 抽象类
        只暴露两个接口给外部, 内部线程和子进程差异对外部透明
    """

    @abstractmethod
    def load_extension(self):
        """装载扩展"""
        pass

    @abstractmethod
    def unload_extension(self):
        """卸载扩展"""
        pass

    @abstractmethod
    def get_extension_info(self):
        """获取扩展信息, 用于Capture流程中传递使用"""
        pass


    @staticmethod
    def create_extension_by_config(config):
        if config.get('extension_type') is None:
            raise ValueError("extension_type is None")

        if config.get('extension_type') == ExtensionType.PROXY:
            from core.extension.impl.proxy.interface.proxy_extension import ProxyExtension
            return ProxyExtension.create_extension_by_config(config)
        elif config.get('extension_type') == ExtensionType.TOR:
            raise ValueError(f"暂不支持 Tor")
        else:
            raise ValueError(f"不支持的扩展类型: {config.get('extension_type').value()}")

        pass



class ExtensionThread(BetterThread, Extension, metaclass=ABCMeta):
    """
    ExtensionThread 使用线程创建
    """
    pass



class ExtensionSubProcess(OuterSubProcessHelper, Extension, metaclass=ABCMeta):
    """
    ExtensionSubProcess 使用外部子进程方式创建
    """
    pass
