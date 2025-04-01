__doc__="pcap连接过滤"
__author__="Li Qingyun"
__date__="2025-03-07"

import stat

from scapy.all import *
from scapy.layers.inet import TCP, UDP, IP
from scapy.layers.inet6 import IPv6
from pathlib import Path
from typing import List

from scapy.layers.l2 import Ether

from core.sniffer.connection.model.connection import Connection
from core.util.io.log_util import LogUtil


class ConnectionsFilter:
    def __init__(self, pcap_path: str, connections_list: List[Connection]):
        """
        :param pcap_path: 要过滤的 pcap 文件路径
        :param connections_list: Connection 对象列表
        """
        self.pcap_path = Path(pcap_path)
        self.connections = connections_list
        self._connection_set = self._build_connection_set()


    @staticmethod
    def filter_pcap(pcap_path: str, connections_list: List[Connection]):
        """
        外部可以直接调用这个静态方法：过滤 pcap 文件
        :param pcap_path: 要过滤的 pcap 文件路径
        :param connections_list: Connection 对象列表
        """
        conn_filter = ConnectionsFilter(pcap_path, connections_list)
        conn_filter.filter_and_overwrite()


    def _build_connection_set(self) -> set:
        """
        生成连接四元组的正反向集合
            同时匹配连接的正向 (local→remote) 和反向 (remote→local) 流量
            使用集合 (set) 存储连接指纹，实现 O(1) 时间复杂度查找
        """
        conn_set = set()
        for conn in self.connections:
            # 正向：local -> remote
            forward = (
                conn.local_ip, conn.local_port,
                conn.remote_ip, conn.remote_port
            )
            # 反向：remote -> local
            backward = (
                conn.remote_ip, conn.remote_port,
                conn.local_ip, conn.local_port
            )

            # todo: 如需根据连接状态（如仅保留 ESTABLISHED 阶段流量, 在这里添加过滤条件

            conn_set.add(forward)
            conn_set.add(backward)

        return conn_set


    def _get_packet_key(self, pkt: Packet) -> tuple:
        """
        从数据包提取四元组
            支持 IPv4/IPv6 和 TCP/UDP 协议
            跳过非 IP 和非 TCP/UDP 数据包
        :param pkt:
        :return:
        """
        src_ip = None
        src_port = None
        dst_ip = None
        dst_port = None

        try:
            # 提取 IP 层
            if pkt.haslayer(IP):
                ip_layer = pkt[IP]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
            elif pkt.haslayer(IPv6):
                ip_layer = pkt[IPv6]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
            else:
                raise ValueError("数据包不是 IP 或 IPv6 协议")

            # 提取端口
            if pkt.haslayer(TCP):
                src_port = pkt[TCP].sport
                dst_port = pkt[TCP].dport
            elif pkt.haslayer(UDP):
                src_port = pkt[UDP].sport
                dst_port = pkt[UDP].dport
            else:
                raise ValueError("数据包不是 TCP 或 UDP 协议")
        except Exception as e:
            # LogUtil().error('main', e, ':', pkt)
            pass


        return src_ip, src_port, dst_ip, dst_port


    def filter_and_overwrite(self):
        """执行过滤并覆盖原始文件"""
        # 读取原始数据包
        packets = rdpcap(str(self.pcap_path))

        # 过滤数据包
        filtered = []
        for pkt in packets:
            key = self._get_packet_key(pkt)
            if key and key in self._connection_set:
                # 确保数据包包含链路层类型
                if not pkt.haslayer(Ether):
                    pkt = Ether() / pkt  # 添加 Ether 层
                filtered.append(pkt)

        # 安全写入临时文件
        temp_path = self.pcap_path.with_suffix(".tmp")
        wrpcap(str(temp_path), filtered, linktype=1)

        # 等待一段时间，确保文件句柄被释放
        time.sleep(0.2)  # 可根据实际情况调整延迟时间

        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                # 原子化替换原文件
                temp_path.replace(self.pcap_path)
                LogUtil().debug('main',
                                f"已过滤并覆盖文件: {self.pcap_path} (保留包数: {len(filtered)}/{len(packets)})")
                break
            except PermissionError:
                retry_count += 1
                time.sleep(1)  # 每次重试前等待1秒
                if retry_count == max_retries:
                    LogUtil().error('main', f"无法替换文件 {self.pcap_path}，达到最大重试次数")



# 使用示例
if __name__ == "__main__":
    # 假设已通过 ConnectionTracker 获取 connections
    connections = [
        Connection(local_ip="192.168.1.100", local_port=54321,
                   remote_ip="93.184.216.34", remote_port=443),
        Connection(local_ip="10.0.0.2", local_port=5353,
                   remote_ip="224.0.0.251", remote_port=5353)
    ]

    # 执行过滤
    _filter = ConnectionsFilter("original.pcap", connections)
    _filter.filter_and_overwrite()
