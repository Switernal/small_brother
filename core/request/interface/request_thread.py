__doc__="请求线程"
__author__="Li Qingyun"
__date__="2025-03-07"

from abc import ABC, abstractmethod

from core.request.const.request_type import RequestType
from core.util.multithreading.better_thread import BetterThread


class RequestThread(BetterThread, ABC):

    def __init__(self, task_name: str, request_name: str):
        super().__init__(name=f"RequestThread-{request_name}")
        self.task_name = task_name
        self.request_name = request_name

    @abstractmethod
    def create_request(self):
        """创建请求"""
        pass

    @abstractmethod
    def send_request(self):
        """发送请求"""
        pass

    @abstractmethod
    def end_request(self):
        """终止请求"""
        pass


    @abstractmethod
    def get_request_thread_info(self):
        """获取Request线程信息"""
        pass


    @staticmethod
    @abstractmethod
    def create_request_thread_by_config(task_name: str, request_name: str, config: dict):
        if config.get('request_type') is None:
            raise ValueError("request_type is None")
        # Chrome 单标签
        if config.get('request_type') == RequestType.BROWSER_CHROME_SINGLE_TAB:
            from core.request.impl.browser.chrome_single_tab_request import ChromeSingleTabRequest
            return ChromeSingleTabRequest.create_request_thread_by_config(task_name=task_name,
                                                                          request_name=request_name,
                                                                          config=config)
        # Chrome 多标签
        elif config.get('request_type') == RequestType.BROWSER_CHROME_MULTI_TAB:
            from core.request.impl.browser.chrome_multi_tab_request import ChromeMultiTabRequest
            return ChromeMultiTabRequest.create_request_thread_by_config(task_name=task_name,
                                                                         request_name=request_name,
                                                                         config=config)
        # 其他请求暂不支持, 可参考 RequestType 列表
        else:
            raise ValueError(f"不支持的请求类型: {config.get('request_type').value()}")

