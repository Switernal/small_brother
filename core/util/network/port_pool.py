__doc__ = "端口池"
__author__ = "Li Qingyun"
__date__ = "2025-02-25"


import threading
from time import sleep

from core.util.io.log_util import LogUtil
from core.util.python.singleton_util import Singleton


@Singleton
class PortPool:
    def __init__(self):
        """
        初始化端口池。
        # :param start_port: 起始端口号
        # :param end_port: 结束端口号
        """
        # self.available_ports = set(range(start_port, end_port + 1))
        self.available_ports = set(range(7890, 8011))   # 实际可用端口是 7890-8010
        self.allocated_ports = set()
        self.lock = threading.Lock()

    def get_port(self):
        """
        从池中获取一个空闲端口
            如果没有端口, 采用指数退避法等待
            todo: 可能造成死锁, 未确认

        :return: 分配的端口号
        """
        wait_time = 0.5
        while True or wait_time < 10:
            with self.lock:
                # if not self.available_ports:
                #     return None  # 没有可用端口
                # 如果
                sleep(1)
                if len(self.available_ports) <= 0:
                    LogUtil().debug('main', f'[port_pool] 端口池中没有可用端口, 等待{wait_time}s后重新获取...')
                    sleep(wait_time)
                    wait_time = wait_time * 1.75    # 指数退避
                    continue

                port = self.available_ports.pop()
                self.allocated_ports.add(port)
                LogUtil().debug('main', f'[port_pool] 申请了一个新的端口号: {port}')
                return port

    def release_port(self, port):
        """
        回收一个端口，将其标记为可用。
        :param port: 要回收的端口号
        """
        with self.lock:
            if port in self.allocated_ports:
                self.allocated_ports.remove(port)
                self.available_ports.add(port)
                LogUtil().debug('main', f'[port_pool] 回收了一个端口号: {port}')
            else:
                raise ValueError(f"Port {port} is not allocated or already released")

    def __str__(self):
        """
        返回端口池的当前状态。
        """
        with self.lock:
            return f"[port_pool] Available ports: {self.available_ports}, Allocated ports: {self.allocated_ports}"


# 示例用法
if __name__ == "__main__":
    # 初始化端口池，端口范围是 8000 到 8005
    port_pool = PortPool(8000, 8005)

    # 单例模式
    PortPool().get_port()
    PortPool().release_port(7890)

    # 获取端口
    port1 = port_pool.get_port()
    port2 = port_pool.get_port()
    LogUtil().debug('main', f"Allocated ports: {port1}, {port2}")
    LogUtil().debug('main', port_pool)

    # 回收端口
    port_pool.release_port(port1)
    LogUtil().debug('main', f"Released port: {port1}")
    LogUtil().debug('main', port_pool)

    # 再次获取端口
    port3 = port_pool.get_port()
    LogUtil().debug('main', f"Allocated port: {port3}")
    LogUtil().debug('main', port_pool)