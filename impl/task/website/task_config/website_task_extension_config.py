__doc__='网站任务扩展配置'
__author__='Li Qingyun'
__date__='2025-03-10'

from core.extension.const.extension_type import ExtensionType
from core.extension.impl.proxy.const.protocol_stack import ProtocolStack, ControlProtocol, SecurityProtocol, \
    TransportProtocol
from core.extension.impl.proxy.const.proxy_type import ProxyType
from core.task.interface.config.task_extension_config import TaskExtensionConfig


class WebsiteTaskExtensionConfig(TaskExtensionConfig):

    def __init__(self,
                 config_dict: dict,
                 ):
        super().__init__(config_dict=config_dict)
        pass


    @staticmethod
    def from_dict(origin_extension_config_dict: dict):
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
            # 2.1 代理类型
            if origin_extension_config_dict.get("proxy_type"):
                proxy_type = ProxyType(origin_extension_config_dict.get("proxy_type"))
                extension_config_dict.update({'proxy_type': proxy_type})
            else:
                raise ValueError("代理类型不能为空")

            # 2.2 协议栈
            if origin_extension_config_dict.get("protocol_stack"):
                protocol_stack_dict = origin_extension_config_dict.get("protocol_stack")
                protocol_stack = ProtocolStack.from_dict(protocol_stack_dict)
                extension_config_dict.update({'protocol_stack': protocol_stack})
            else:
                raise ValueError("协议栈不能为空")

        # elif extension_type == ExtensionType.TOR:
            # 2.2 tor类型
        else:
            raise ValueError(f"[WebsiteTaskExtensionConfig] 扩展类型 {extension_type.value} 不支持")

        return WebsiteTaskExtensionConfig(config_dict=extension_config_dict)


    def to_dict(self) -> dict:
        extension_config_dict = {}
        extension_config_dict.update({'extension_type': self.config_dict.get("extension_type").value})

        if self.config_dict.get("extension_type") == ExtensionType.PROXY:
            # 1. 代理类型
            extension_config_dict.update({'proxy_type': self.config_dict.get("proxy_type").value})
            extension_config_dict.update({'protocol_stack': self.config_dict.get("protocol_stack").to_dict()})
        # elif self.config_dict.get("extension_type") == ExtensionType.TOR:
            # 2. tor类型

        return extension_config_dict