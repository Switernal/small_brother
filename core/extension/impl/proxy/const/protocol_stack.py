__doc__ = '协议栈'
__auther__ = 'Li Qingyun'
__date__ = '2025-02-24'

import enum

from core.util.io.log_util import LogUtil


class ControlProtocol(enum.Enum):
    """
    加密代理-控制层协议
    """
    SS = 'shadowsocks'
    VLESS = 'vless'
    VMESS = 'vmess'
    TROJAN = 'trojan'
    HY2 = 'hysteria2'
    TUIC = 'tuic'
    SOCKS = 'socks'
    HTTP = 'http'


class SecurityProtocol(enum.Enum):
    """
    加密代理-安全层协议
    """
    TLS = 'tls'       # TLS (默认支持TLS 1.2及以上或其他情况)
    TLS12 = 'tls12'   # 仅支持到 TLS 1.2 (不支持TLS 1.3)
    TLS13 = 'tls13'   # 仅支持 TLS 1.3 (不支持TLS 1.2)
    XTLS = 'xtls'                                   # 纯xtls(已废弃, 目前应该没有在使用中的)
    XTLS_VISION = 'xtls-rprx-vision'                # 仅vision流控, 非udp-443版本
    REALITY = 'reality'                             # 纯reality, 无vision流控
    REALITY_VISION = 'reality-xtls-rprx-vision'     # reality+vision流控
    NONE = 'none'  # 无额外安全协议(通常是控制层自带加密, 如vmess, ss)


class TransportProtocol(enum.Enum):
    """
    加密代理-传输层协议
    """
    TCP = 'tcp'
    UDP = 'udp'
    WS = 'websocket'
    QUIC = 'quic'
    mKCP = 'mkcp'
    HTTP2 = 'http2'
    gRPC = 'grpc',
    XHTTP = 'xhttp'


class ProtocolStack:
    """
    协议栈
        用于描述一个加密代理节点的协议栈
        同时包含远程代理节点的地址和端口
    """
    def __init__(self,
                 control: ControlProtocol,
                 security: SecurityProtocol,
                 transport: TransportProtocol,
                 remote_address: str,
                 remote_port: int
                 ):
        self.control = control
        self.security = security
        self.transport = transport
        self.remote_address = remote_address      # 代理服务器地址
        self.remote_port = remote_port            # 代理服务器端口


    def validation_check(self):
        """检查协议合法性"""
        try:
            if isinstance(self.control, ControlProtocol) is False:
                raise TypeError('Control协议类型错误')
            if isinstance(self.security, SecurityProtocol) is False:
                raise TypeError('Security协议类型错误')
            if isinstance(self.transport, TransportProtocol) is False:
                raise TypeError('Transport协议类型错误')
        except Exception as e:
            LogUtil().error('main', e.__str__())
            return False
        return True


    @staticmethod
    def from_dict(protocol_stack_dict):
        """
        从字典构建协议栈
        :param protocol_stack_dict: 协议栈字典
            传入的字典示例:
            {
                'control_protocol': 'vless',
                'security_protocol': 'tls',
                'transport_protocol': 'ws',
                'remote_address': '192.168.1.1',
                'remote_port': 443
            }
        :return: 协议栈类型的对象
        """
        return ProtocolStack(
            control=ControlProtocol(protocol_stack_dict.get('control_protocol')),
            security=SecurityProtocol(protocol_stack_dict.get('security_protocol')),
            transport=TransportProtocol(protocol_stack_dict.get('transport_protocol')),
            remote_address=protocol_stack_dict.get('remote_address'),
            remote_port=protocol_stack_dict.get('remote_port')
        )

    def to_dict(self):
        """
        从协议栈对象转换成字典(用于存储等)
        :return:
        """
        return {
            'control_protocol': self.control.value,
            'security_protocol': self.security.value,
            'transport_protocol': self.transport.value,
            'remote_address': self.remote_address,
            'remote_port': self.remote_port
        }


    def __str__(self):
        return f'{self.control.value}_{self.security.value}_{self.transport.value}'