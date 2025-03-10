# 用途,作者和日期
__doc__ = "管理代理进程的启动和终止"
__author__ = "Li Qingyun"
__date__ = "2025-02-24"

from time import sleep

from extension.proxy.cores.mihomo.mihomo_proxy import MihomoProxy
from extension.proxy.protocol_stack import ProtocolStack, ControlProtocol, SecurityProtocol, TransportProtocol
from extension.proxy.proxy_type import ProxyType
from utils.port_pool import PortPool


def ProxyManagerSingleton(cls):
    """单例模式修饰类"""
    # 创建一个字典用来保存被装饰类的实例对象

    _instance = {}
    def _singleton(*args, **kwargs):
        # 判断这个类有没有创建过对象，没有新创建一个，有则返回之前创建的
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return _singleton


@ProxyManagerSingleton
class ProxyManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):
        # 所有已经打开的代理, { 代理类型+协议栈: 代理对象 }
        self.proxys = {}


    def create_proxy(self,
                     proxy_type: ProxyType,
                     protocol_stack: ProtocolStack,
                     log_file_dir: str
                     ):
        """
        使用代理类型+协议栈的方式创建一个代理
        :param log_file_dir: 日志文件目录
        :param proxy_type: 代理类型
        :param protocol_stack: 协议栈
        :return:
        """
        proxy = None
        # 根据"代理软件类型+协议栈"创建代理
        if proxy_type == ProxyType.MIHOMO:
            # 创建一个mihomo代理对象, 传入一个新端口号, 以及一个协议栈
            new_port = PortPool().get_port()
            proxy = MihomoProxy(port=new_port, protocol_stack=protocol_stack, log_file_dir=log_file_dir)
        elif proxy_type == ProxyType.V2RAY:
            raise ValueError(f"[ProxyManager] 暂不支持创建{proxy_type.value}代理")
            pass
        elif proxy_type == ProxyType.XRAY:
            raise ValueError(f"[ProxyManager] 暂不支持创建{proxy_type.value}代理")
            pass
        else:
            raise ValueError("[ProxyManager] 不支持的代理类型")

        # 添加到dict里
        self.proxys.update({new_port: proxy})

        print(f'[ProxyManager] 已成功创建一个 {proxy_type.value} 代理, 端口: {proxy.port}')
        # return proxy  # 不返回对象了, 只返回端口
        return proxy.port


    def get_proxy(self, port: int):
        """
        获取一个代理对象, 如果存在就直接返回, 如果不存在则创建一个
        :param port:
        :return:
        """
        # 如果存在创建过的代理, 就无需重复创建了
        # 命名方式是代理类型和协议栈的组合
        if self.proxys.get(port) is not None:
            # print(f"端口 {port} 代理已存在, 无需重复创建")
            return self.proxys.get(port)
        else:
            raise ValueError(f"[ProxyManager] 端口 {port} 上不存在代理, 请先创建")


    def close_proxy(self, port: int):
        if self.proxys.get(port) is not None:
            # 先关闭
            self.proxys.get(port).stop()
            # 再删除
            self.proxys.pop(port)
            # 回收端口
            PortPool().release_port(port)
            print(f"[ProxyManager] 端口 {port} 代理已关闭")
        else:
            print(f"[ProxyManager] 端口 {port} 代理不存在, 无需关闭")



if __name__ == '__main__':
    # mihomo
    mihomo_port = ProxyManager().create_proxy(
                                proxy_type=ProxyType.MIHOMO,
                                protocol_stack=ProtocolStack(
                                    control=ControlProtocol.VLESS,
                                    security=SecurityProtocol.REALITY_VISION,
                                    transport=TransportProtocol.TCP,
                                    remote_address="23.106.154.40",
                                    remote_port=59932
                                ),
                                log_file_dir="/tmp"
    )
    ProxyManager().get_proxy(mihomo_port).start()
    sleep(15)
    ProxyManager().get_proxy(mihomo_port).stop()

    # xray
    xray_port = ProxyManager().create_proxy(
        proxy_type=ProxyType.XRAY,
        protocol_stack=ProtocolStack(
            control=ControlProtocol.VLESS,
            security=SecurityProtocol.REALITY_VISION,
            transport=TransportProtocol.TCP,
            remote_address="23.106.154.40",
            remote_port=59932
        ),
        log_file_dir="/tmp"
    )
    ProxyManager().get_proxy(xray_port).start()
    sleep(15)
    ProxyManager().get_proxy(xray_port).stop()