__doc__='外部子进程类'
__auther__='Li Qingyun'
__date__='2025-03-01'

import signal

from core.util.io.log_util import LogUtil

"""
    注: 这个类封装了一个子进程类, 用于创建子进程
        主要用于启动外部进程, 而非 Python 进程
"""


import subprocess
from abc import abstractmethod


class OuterSubProcessHelper:
    """
    外部子进程助手类
    """

    def __init__(self,
                 name: str,
                 start_command,
                 logger_name: str='main',
                 enable_log: bool=False,
                 log_file_path: str = None,
                 ):
        """
        初始化
        :param logger_name:     日志记录器名称
        :param name:            进程名
        :param start_command:   启动命令
        :param enable_log:      是否启用日志
        :param log_file_path:   日志文件路径
        """
        self.logger_name = logger_name        # 日志记录器名称
        self.name = name                      # 自定义的进程名
        self.enable_log = enable_log          # 是否启用日志
        self.log_file_path = log_file_path    # 日志目录(如果不启用, 这一项可以为None)
        self.__start_command:list = start_command  # 启动命令
        self.__log_file = None                # 日志文件对象
        self.__process = None                 # 进程
        self.__status = None                  # 进程状态

        # self.stop_command = None              # 停止命令
        pass


    @staticmethod
    def quick_execute_cmd(cmd):
        """
        快速执行命令
        :param cmd: 命令
        :return: 执行结果
        """
        result = None
        try:
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        except Exception as e:
            LogUtil().error('main', f'[ProcessHelper.quick_execute_cmd()] 执行命令 {cmd} 失败, 原因: {e}')
        finally:
            if result is not None:
                return result.returncode == 0
            else:
                return False


    @property
    def status(self):
        """获取进程状态"""
        if self._is_process_exist() is True:
            return self.__process.poll()

        return None


    @property
    def pid(self):
        """进程pid"""
        if self._is_process_exist() is False:
            return None
        return self.__process.pid


    def _is_process_exist(self):
        """
        判断进程是否存在
        :return: 是否存在
        """
        if self.__process is not None:
            return True
        else:
            return False


    def _is_process_alive(self):
        """
        判断线程是否存活
        :return:
        """
        if self._is_process_exist() is True:
            if self.__status is None:   # 状态为None代表进程还在运行
                return True

        return False


    def start_process(self):
        """
        启动进程
        :param
        :return:
        """
        LogUtil().debug(self.logger_name, f"[OuterSubProcessHelper(name: {self.name}).open()] 启动中...")
        # 标准输出需要看是否启用日志
        std_out = None
        if self.enable_log is True:
            # 启用日志, 则输出到文件
            self.__log_file = open(self.log_file_path, "w")
            std_out = self.__log_file
        else:
            # 不启用日志就到标准输出
            std_out = subprocess.PIPE

        # 启动进程
        self.__process = subprocess.Popen(
            self.__start_command,      # 启动命令
            stdout=std_out,            # 将标准输出重定向
            stderr=subprocess.STDOUT,  # 将标准错误重定向到标准输出
            text=True,  # 以文本模式处理输出
        )
        LogUtil().debug(self.logger_name, f"[OuterSubProcessHelper(name: {self.name}).open()] 已启动, PID: {self.pid}")
        pass


    def _terminate_process(self):
        """
        kill进程
        流程: 先检查系统中pid是否存在,如果存在, 则执行kill, 并返回kill成功与否
        :return:
        """
        if self._is_process_alive():
            try:
                # 关闭日志
                self._close_log_file()
                # 终止进程
                LogUtil().debug(self.logger_name, f"[OuterSubProcessHelper(name: {self.name})._kill()] 正在尝试终止进程")
                # self.__process.terminate() # terminate 会直接中断, 可能会导致程序数据写入丢失
                # self.__process.wait()       # todo: 不确定这个要不要加
                # 发送停止信号, 模拟Ctrl-C退出
                self.__process.send_signal(signal.SIGINT)
                # 获取终止后的输出
                output_message = self.__process.communicate()[0]
                LogUtil().info(self.logger_name, f"[OuterSubProcessHelper(name: {self.name})._kill()] 进程终止后的输出: {output_message}")
                return True
            except Exception as e:
                LogUtil().error(self.logger_name, f"[OuterSubProcessHelper(name: {self.name})._kill()] 终止时发生异常: {e}")
                return False
        else:
            LogUtil().warning(self.logger_name, f"[OuterSubProcessHelper(name: {self.name})._kill()] 进程不处于存活状态, 无需终止")
            return True
        pass


    def stop_process(self):
        LogUtil().debug(self.logger_name, f'[OuterSubProcessHelper.start()] 进程 {self.name} 正在准备停止')
        self._terminate_process()
        # 如果启用了日志, 就处理一下
        if self.enable_log is True:
            LogUtil().debug(self.logger_name, f'[OuterSubProcessHelper.start()] 进程 {self.name} 处理日志')
            self.handle_log()


    @abstractmethod
    def handle_log(self):
        """处理日志的方法"""
        pass


    def _close_log_file(self):
        """
        关闭日志文件
        :return:
        """
        if self.enable_log and self.enable_log is False:
            return # 如果没有启用日志, 直接返回
        if self.__log_file is not None and self.__log_file.closed is False:
            self.__log_file.close()


    def __del__(self):
        # 如果对象意外回收了, 也要终止进程
        self._close_log_file()      # 关闭日志文件
        self.stop_process()
        if self._is_process_alive():
            self.__process.wait()       # 等待进程终止
