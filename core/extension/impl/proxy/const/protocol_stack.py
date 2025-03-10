__doc__ = '协议栈'
__auther__ = 'Li Qingyun'
__date__ = '2025-02-24'

import enum


class ControlProtocol(enum.Enum):
    """
    控制层
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
    安全层
    """
    TLS = 'tls'       # TLS (默认支持TLS 1.2及以上或其他情况)
    TLS12 = 'tls12'   # 仅支持到 TLS 1.2 (不支持TLS 1.3)
    TLS13 = 'tls13'   # 仅支持 TLS 1.3 (不支持TLS 1.2)
    XTLS = 'xtls'     # 纯xtls(已废弃, 目前应该没有在使用中的)
    XTLS_VISION = 'xtls-rprx-vision'    # 仅vision流控, 非udp-443版本
    REALITY = 'reality'                 # 纯reality, 无vision流控
    REALITY_VISION = 'reality-xtls-rprx-vision'
    NONE = 'no-extra-security'


class TransportProtocol(enum.Enum):
    """
    传输层
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
            print(e)
            return False
        return True

    @staticmethod
    def from_dict(protocol_stack_dict):
        return ProtocolStack(
            control=ControlProtocol(protocol_stack_dict.get('control_protocol')),
            security=SecurityProtocol(protocol_stack_dict.get('security_protocol')),
            transport=TransportProtocol(protocol_stack_dict.get('transport_protocol')),
            remote_address=protocol_stack_dict.get('remote_address'),
            remote_port=protocol_stack_dict.get('remote_port')
        )

    def to_dict(self):
        return {
            'control_protocol': self.control.value,
            'security_protocol': self.security.value,
            'transport_protocol': self.transport.value,
            'remote_address': self.remote_address,
            'remote_port': self.remote_port
        }


    def __str__(self):
        return f'{self.control.value}_{self.security.value}_{self.transport.value}'


if __name__ == '__main__':
    print(ControlProtocol('vless'))