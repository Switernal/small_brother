__doc__="Extension 抽象类"
__author__="Li Qingyun"
__date__="2025-03-09"

from abc import abstractmethod, ABCMeta

from core.extension.const.extension_type import ExtensionType
from core.util.multiprocessing.outer_subprocess_helper import OuterSubProcessHelper
from core.util.multithreading.better_thread import BetterThread


class Extension(metaclass=ABCMeta):
    """
    Extension 抽象类 (纯虚类, 不可实例化)
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
        """
        根据配置创建扩展
        :param config:
        :return:
        """
        if config.get('extension_type') is None:
            raise ValueError("[Extension] extension_type 不存在")

        extension_type = config.get('extension_type')

        # 1. 代理
        if extension_type == ExtensionType.PROXY:
            from core.extension.impl.proxy.interface.proxy_extension import ProxyExtension
            return ProxyExtension.create_extension_by_config(config)
        # 2. Tor
        elif extension_type == ExtensionType.TOR:
            raise ValueError(f"[Extension] 暂不支持 Tor")
        # 3. 其他
        else:
            raise ValueError(f"[Extension] 不支持的扩展类型: {extension_type.value}")

        pass



class ExtensionThread(BetterThread, Extension, metaclass=ABCMeta):
    """
    使用内部子线程创建 Extension
        todo: 暂时没有实现类继承这个. 另外如果需要用的话, CaptureThread 内的代码要做对应支持
    """
    pass



class ExtensionSubProcess(OuterSubProcessHelper, Extension, metaclass=ABCMeta):
    """
    使用外部子进程方式创建 Extension
        一般使用这个, 因为代理软件都是外部的二进制可执行文件, 通过命令行方式启动
    """
    pass
