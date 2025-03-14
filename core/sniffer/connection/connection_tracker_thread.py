import threading

import psutil
import time
import socket
import json
from datetime import datetime

from typing import Dict

from core.sniffer.connection.model.connection import Connection
from core.util.io.log_util import LogUtil
from core.util.io.path_util import PathUtil
from core.util.multithreading.better_thread import BetterThread
from core.util.string.time_util import TimeUtil


class ConnectionTrackerThread(BetterThread):
    """
    连接追踪器
    """

    def __init__(self,
                 task_name,
                 pid: int,
                 log_file_dir: str,
                 log_file_name=None
                 ):
        super().__init__()
        
        self.task_name = task_name

        # 文件相关
        self.log_file_dir = log_file_dir
        self.log_file_name = log_file_name
        self.log_file_path = None

        # 连接相关
        self.pid = pid          # pid
        self.connections_dict: Dict[str, Connection] = {}  # 所有连接（含历史）
        self.process = psutil.Process(pid)            # 进程
        self.hostname_cache = {}                      # DNS缓存

        self.interval = 0.5       # 轮询间隔

        # 设置多线程相关
        self.daemon = True                    # 设为守护线程, 主线程终止会带着子线程一起停
        self.name = 'ConnectionTracker'       # 线程名


    def run(self):
        self._start_monitor()


    def stop(self):
        super().stop()
        self.join()


    def get_connections_list(self) -> [Connection]:
        """
        获取连接列表
        :return:
        """
        return self.connections_dict.values()


    def _reverse_dns(self, ip: str) -> str:
        """带缓存的DNS反向查询"""
        if ip not in self.hostname_cache:
            try:
                host = socket.gethostbyaddr(ip)[0]
                self.hostname_cache[ip] = host
            except (socket.herror, socket.gaierror):
                self.hostname_cache[ip] = ip
        return self.hostname_cache[ip]


    def _update_connections(self):
        """更新当前所有连接状态"""
        # 用于保存当前活跃的连接
        current_active_conns = {}

        connections = self.process.connections(kind='inet')
        # 遍历当前所有连接
        for conn in connections:

            # 如果连接没有远程地址, 说明没有创立连接, 调过
            if not conn.raddr:
                continue

            local = conn.laddr      # 本地ip
            remote = conn.raddr     # 远程ip
            status = conn.status    # 连接状态

            # 构造唯一键
            conn_key = Connection.generate_key(local.ip, local.port, remote.ip, remote.port)

            # 创建/更新连接对象
            if conn_key not in self.connections_dict:
                # 如果连接不在列表里, 说明是新连接
                new_conn = Connection(
                    local_ip=local.ip,
                    local_port=local.port,
                    remote_ip=remote.ip,
                    remote_port=remote.port
                )
                new_conn.status_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "status": status
                })
                self.connections_dict[conn_key] = new_conn
                LogUtil().debug(self.task_name, f"[ConnectionTracker] 新建连接 [{status}]: {new_conn.local_ip}:{new_conn.local_port} -> {new_conn.remote_ip}:{new_conn.remote_port}")
            else:
                existing = self.connections_dict[conn_key]
                existing.last_seen = time.time()
                existing.active = True
                if existing.status_history[-1]["status"] != status:
                    existing.status_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "status": status
                    })
                    LogUtil().debug(self.task_name, f"[ConnectionTracker] 连接状态变更 [{status}]: {existing.local_ip}:{existing.local_port} -> {existing.remote_ip}:{existing.remote_port}")

            # 添加到当前活跃的连接
            current_active_conns[conn_key] = True

        # 如果保存的连接不在当前活跃连接里, 标记为不活跃
        for conn_key in self.connections_dict:
            if conn_key not in current_active_conns:
                self.connections_dict[conn_key].active = False


    def _save_to_file(self):
        """持久化保存到JSON文件"""

        # 如果没有传入文件名, 则使用默认的文件名
        if self.log_file_name is None:
            self.log_file_name = f"connections_{TimeUtil.now_time_str()}_pid={self.pid}.json"

        self.log_file_path = PathUtil.file_path_join(self.log_file_dir, file_path=self.log_file_name)

        data = []
        for conn in self.connections_dict.values():
            data.append({
                "local": {
                    'ip': conn.local_ip,
                    'port': conn.local_port
                },
                "remote": {
                    "ip": conn.remote_ip,
                    "port": conn.remote_port,
                    "hostname": self._reverse_dns(conn.remote_ip)
                },
                "first_seen": datetime.fromtimestamp(conn.first_seen).isoformat(),
                "last_seen": datetime.fromtimestamp(conn.last_seen).isoformat(),
                "active": conn.active,
                "status_history": conn.status_history
            })
        with open(self.log_file_path, 'w') as file:
            json.dump(data, file, indent=2)
        LogUtil().debug(self.task_name, f"[ConnectionTracker] 连接历史已保存至 {self.log_file_name}")


    def _start_monitor(self):
        """启动监控循环"""
        try:
            LogUtil().debug(self.task_name, f"[ConnectionTracker] 开始监控进程 {self.pid} (轮询间隔 {self.interval}s)...")
            while self.stop_event.is_set() is False:
                self._update_connections()
                time.sleep(self.interval)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            LogUtil().debug(self.task_name, f"[ConnectionTracker] 进程 {self.pid} 已终止或权限不足")
        finally:
            self._save_to_file()


    def clear(self):
        """
        继承自BetterThread的方法，用于清理资源
        :return:
        """
        pass


    def get_connection_tracker_thread_info(self):
        """
        获取连接追踪线程的信息。

        该方法返回一个字典，包含了当前连接追踪线程的相关信息，包括进程ID（pid）、日志文件路径（log_file_path）
        以及连接信息（connections）。这些信息主要用于监控和调试目的，帮助开发者了解当前线程的运行状态和连接情况。

        :return: 包含连接追踪线程信息的字典。
        """
        return {
            "pid": self.pid,
            "log_file_path": self.log_file_path,
            "connections": self.connections_dict,
        }
        pass


    @staticmethod
    def create_connection_tracker_thread_by_config(task_name: str, config: dict):
        """
        根据配置dict创建线程
        :param task_name:
        :param config:
        :return:
        """
        if config is None:
            raise ValueError('[ConnectionTrackerThread] task_config 不能为空')
        if config.get('log_file_dir') is None:
            raise ValueError("[ConnectionTrackerThread] task_config['log_file_dir'] 不能为空")
        return ConnectionTrackerThread(
            task_name=task_name,
            pid=config.get('pid'),
            log_file_dir=config.get('log_file_dir'),
            log_file_name=config.get('log_file_name')
        )