from dataclasses import dataclass, field
import time
from typing import List, Dict


@dataclass
class Connection:
    """网络连接对象，记录完整生命周期"""
    local_ip: str
    local_port: int
    remote_ip: str
    remote_port: int
    status_history: List[Dict[str, str]] = field(default_factory=list)  # 状态变更历史
    first_seen: float = field(default_factory=time.time)  # 首次发现时间戳
    last_seen: float = field(default_factory=time.time)   # 最后发现时间戳
    active: bool = True  # 是否仍存在

    @property
    def key(self) -> str:
        """唯一标识符：协议+本地+远程地址"""
        return f"{self.local_ip}:{self.local_port}->{self.remote_ip}:{self.remote_port}"

    @staticmethod
    def generate_key(local_ip, local_port, remote_ip, remote_port):
        return f"{local_ip}:{local_port}->{remote_ip}:{remote_port}"


    def __str__(self):
        return f"Connection({self.local_ip}:{self.local_port} -> {self.remote_ip}:{self.remote_port})"