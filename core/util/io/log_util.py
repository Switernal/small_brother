__doc__='日志记录工具'
__author__='Li Qingyun'
__date__='2025-03-13'

import logging
import threading

from core.util import PathUtil
from core.util.python.singleton_util import Singleton
from core.util.string.time_util import TimeUtil

@Singleton
class LogUtil:
    """
    日志记录工具
    """
    
    def __init__(self):
        self.enable_log = True                  # 是否启用日志记录
        self.log_dir = None                     # 日志路径
        self.__loggers = {}                     # 日志记录器对象, key是任务名, value是logger对象
        self.__logger_locks = {}                # 日志记录器锁, key是任务名, value是锁对象
        self.__util_lock = threading.Lock()     # 工具锁


    def set_log_dir(self, log_dir: str):
        """
        设置日志路径
        :param log_dir:
        :return:
        """
        self.log_dir = log_dir


    def get_logger(self, logger_name: str):
        """
        获取 logger
        :param logger_name: logger 名称
        :return:
        """

        # 如果已经存在日志记录器, 直接返回
        if self.__loggers.get(logger_name) is not None:
            return self.__loggers.get(logger_name)

        # print(f"[LogUtil] 创建日志记录器: {logger_name}")

        # 必须先拿到工具锁, 才能创建Logger锁, 避免Logger锁重复创建
        with self.__util_lock:
            # 创建Logger锁
            if self.__logger_locks.get(logger_name) is None:
                self.__logger_locks.update({logger_name: threading.Lock()})
                # print(f"[LogUtil] 创建日志记录器锁: {logger_name}")

        # print(f"[LogUtil] 创建日志记录器: {logger_name}")

        # 有了线程锁才能创建Logger, 避免重复创建
        with self.__logger_locks.get(logger_name):
            # print(f"[LogUtil] 创建日志记录器: {logger_name}")

            # 如果不存在日志记录器, 创建日志记录器
            # 1. 记录当前时间
            now_time_str = TimeUtil.now_time_str()
            # 2. 创建记录器文件名称
            logger_file_name = f'{logger_name}_{now_time_str}'
            # 3. 创建记录器
            # 在初始化时关闭根 Logger 的默认处理器
            logging.getLogger().handlers = []
            logging.getLogger().propagate = False

            logger = logging.getLogger(logger_name)

            logger.propagate = False  # 禁用日志传播
            logger.setLevel(logging.INFO)
            # 4. 创建文件处理器
            # 4.1 先检查文件路径是否存在, 不存在用默认, 然后创建目录.
            if LogUtil().log_dir is None:
                LogUtil().log_dir = 'logs'     # 在当前目录下创建logs路径

            PathUtil.auto_create_path(f'{LogUtil().log_dir}')

            file_handler = logging.FileHandler(
                f'{LogUtil().log_dir}/{logger_file_name}.log',
                mode="a",
                encoding="utf-8"
            )
            # 配置日志格式
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)

            # 创建控制台处理器
            # console_handler = logging.StreamHandler()
            # console_handler.setLevel(logging.INFO)
            # console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))


            # 5. 创建控制台处理器
            logger.addHandler(file_handler)
            # logger.addHandler(console_handler)

            # 6. 存储logger对象
            self.__loggers[logger_name] = logger

            # print(f"[LogUtil] 创建日志记录器: {logger_name} 完成")

            return logger


    def info(self, logger_name: str, msg):
        """
        记录一条info级别日志
        :param logger_name:
        :param msg:
        :return:
        """
        if not self.enable_log:
            return
        self.get_logger(logger_name).warning("[INFO] " + msg)   # todo: INFO和DEBUG无法输出的问题暂时解决不了
        if logger_name != 'main':
            self.get_logger('main').warning("[INFO] " + msg)    # todo: INFO和DEBUG无法输出的问题暂时解决不了


    def debug(self, logger_name: str, msg):
        """
        记录一条debug级别日志
        :param logger_name:
        :param msg:
        :return:
        """
        if not self.enable_log:
            return
        self.get_logger(logger_name).warning("[DEBUG] " + msg)   # todo: INFO和DEBUG无法输出的问题暂时解决不了
        if logger_name != 'main':
            self.get_logger('main').warning("[DEBUG] " + msg)    # todo: INFO和DEBUG无法输出的问题暂时解决不了


    def warning(self, logger_name: str, msg):
        """
        记录一条warning级别日志
        :param logger_name:
        :param msg:
        :return:
        """
        if not self.enable_log:
            return
        self.get_logger(logger_name).warning(msg)
        if logger_name != 'main':
            self.get_logger('main').warning(msg)


    def error(self, logger_name: str, msg):
        """
        记录一条error级别日志
        :param logger_name:
        :param msg:
        :return:
        """
        if not self.enable_log:
            return
        self.get_logger(logger_name).error(msg)
        if logger_name != 'main':
            self.get_logger('main').warning(msg)