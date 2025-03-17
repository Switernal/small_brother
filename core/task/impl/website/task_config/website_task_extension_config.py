__doc__='网站任务扩展配置'
__author__='Li Qingyun'
__date__='2025-03-10'

from core.extension.const.extension_type import ExtensionType
from core.extension.impl.proxy.const.protocol_stack import ProtocolStack, ControlProtocol, SecurityProtocol, \
    TransportProtocol
from core.extension.impl.proxy.const.proxy_type import ProxyType
from core.task.interface.task_config.task_extension_config import TaskExtensionConfig


class WebsiteTaskExtensionConfig(TaskExtensionConfig):
    """
    网站任务扩展配置
        该类对象只能作为 TaskThread 中的属性, 用于管理 Extension 配置信息
        具体配置如何解析, 看具体的 Task
    """

    def __init__(self,
                 config_dict: dict,
                 ):
        """

        :param config_dict: 配置 dict
        """
        super().__init__(config_dict=config_dict)
        pass


    @staticmethod
    def from_dict(origin_extension_config_dict: dict):
        """
        从字典中解析出 WebsiteTaskExtensionConfig 对象
        :param origin_extension_config_dict: 原始字典
            注: 这里的字典是从文件中读取的, 所以是原始字典
                里面所有字段都是字符串
                因为TaskThread创建需要用一些信息, 会在此初步将部分字段解析为对象
                因此后面创建代理等位置传入的 dict 里会出现一些对象而非原始字符串
        :return: WebsiteTaskExtensionConfig 对象
        """
        extension_config_dict = {
            # "extension_type": ExtensionType.PROXY,
            # "proxy_type": ProxyType.MIHOMO,
            # "protocol_stack": ProtocolStack(
            #     control=ControlProtocol.VLESS,
            #     security=SecurityProtocol.REALITY_VISION,
            #     transport=TransportProtocol.TCP,
            #     remote_address="23.106.154.40",
            #     remote_port=59932
            # )
        }

        # 1. 扩展类型
        if origin_extension_config_dict.get("extension_type"):
            extension_type = ExtensionType(origin_extension_config_dict.get("extension_type"))
            extension_config_dict.update({'extension_type': extension_type})
        else:
            raise ValueError("扩展类型不能为空")

        # 2. 根据扩展类别
        if extension_type == ExtensionType.PROXY:
            # 2.1 解析代理类型
            if origin_extension_config_dict.get("proxy_type"):
                proxy_type = ProxyType(origin_extension_config_dict.get("proxy_type"))  # 转为 ProxyType 对象
                extension_config_dict.update({'proxy_type': proxy_type})
            else:
                raise ValueError("代理类型不能为空")

            # 2.2 解析协议栈
            if origin_extension_config_dict.get("protocol_stack"):
                protocol_stack_dict = origin_extension_config_dict.get("protocol_stack")
                protocol_stack = ProtocolStack.from_dict(protocol_stack_dict)   # 转为 ProtocolStack 对象
                extension_config_dict.update({'protocol_stack': protocol_stack})
            else:
                raise ValueError("协议栈不能为空")

            # 2.3 代理配置
            if origin_extension_config_dict.get("proxy_config"):
                proxy_config_dict = origin_extension_config_dict.get("proxy_config")    # 仍为原始字符串字典
                extension_config_dict.update({'proxy_config': proxy_config_dict})
            # else:
            #     raise ValueError("代理配置不能为空")

        # elif extension_type == ExtensionType.TOR:
            # todo: 2.2 tor类型

        else:
            raise ValueError(f"[WebsiteTaskExtensionConfig] 扩展类型 {extension_type.value} 不支持")

        return WebsiteTaskExtensionConfig(config_dict=extension_config_dict)


    def to_dict(self) -> dict:
        """
        转 dict, 用于保存到文件
        :return: 扩展配置字典, 里面全是字符串, 可以直接存储到文件
        """

        extension_config_dict = {}
        extension_config_dict.update({'extension_type': self.config_dict.get("extension_type").value})

        if self.config_dict.get("extension_type") == ExtensionType.PROXY:
            # 1. 代理类型
            extension_config_dict.update({'proxy_type': self.config_dict.get("proxy_type").value})  # 由于这里是枚举, 需要取value字符串
            extension_config_dict.update({'protocol_stack': self.config_dict.get("protocol_stack").to_dict()})  # 由于这里是对象, 需要转为字典
            extension_config_dict.update({'proxy_config': self.config_dict.get("proxy_config")})    # 仍为原始字符串字典
        # elif self.config_dict.get("extension_type") == ExtensionType.TOR:
            # todo: 2. tor类型

        return extension_config_dict