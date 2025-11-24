__doc__ = "网卡实用工具"
__author__ = "Li Qingyun"
__date__ = "2025-11-18"

import platform

import psutil
import socket

from core.util.python.singleton_util import Singleton

@Singleton
class NetworkInterfaceUtil:
    def get_active_physical_interface(self):
        """
        获取当前活跃的网卡名称, 多系统适用(已验证 macOS/Windows)
        """
        # 获取网卡状态
        stats = psutil.net_if_stats()
        # 获取网卡流量统计
        io_counters = psutil.net_io_counters(pernic=True)
        # 获取所有网卡地址
        interfaces = psutil.net_if_addrs()

        # 常见虚拟网卡前缀（需要排除）
        exclude_prefixes = ['lo', 'docker', 'veth', 'br-', 'virbr', 'tun', 'tap', 'vmnet']

        candidates = []

        for interface_name, addrs in interfaces.items():
            # 1. 排除虚拟网卡
            if any(interface_name.startswith(prefix) for prefix in exclude_prefixes):
                continue

            # 2. 检查网卡是否处于UP状态
            if interface_name not in stats or not stats[interface_name].isup:
                continue

            # 3. 检查是否有非回环IP地址
            has_valid_ip = False
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    if not addr.address.startswith('127.'):
                        has_valid_ip = True
                        break

            if not has_valid_ip:
                continue

            # 4. 检查是否有网络流量
            if interface_name in io_counters:
                counters = io_counters[interface_name]
                if counters.bytes_sent > 0 or counters.bytes_recv > 0:
                    # 存储接口名和总流量大小
                    total_bytes = counters.bytes_sent + counters.bytes_recv
                    candidates.append((interface_name, total_bytes))

        # 5. 按流量大小排序，返回流量最大的接口
        final_interface_name = None

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            final_interface_name = candidates[0][0]

        # Windows 下,网卡名称需要转换一下, 通常是"以太网X" -> "Intel (R) Ethernet Connection ..."
        if platform.system() == "Windows":
            # 获取Windows接口列表
            from scapy.arch import get_windows_if_list
            interfaces = get_windows_if_list()
            for iface in interfaces:
                # iface['name'] = "以太网X"
                # iface['description'] = "Intel (R) Ethernet Connection ..."
                if iface['name'] == final_interface_name:
                    final_interface_name = iface['description']
                    break

        return final_interface_name


# 示例用法
if __name__ == "__main__":
    active_interface = NetworkInterfaceUtil().get_active_physical_interface()
    print(f"当前活跃的物理网卡: {active_interface}")