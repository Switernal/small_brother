__doc__='网站请求配置类'
__author__='Li Qingyun'
__date__='2025-03-10'

from core.request.const.request_type import RequestType
from core.task.interface.task_config.task_request_config import TaskRequestConfig


class WebsiteTaskRequestConfig(TaskRequestConfig):
    """
    网站请求配置类
        该类对象只能作为 TaskRequestThread 中的属性, 用于管理 Request 配置信息
        具体配置如何解析, 看具体的 TaskRequestThread 实现类
    """

    def __init__(self,
                 config_dict: dict,
                 ):
        """

        :param config_dict: 配置 dict
        """
        super().__init__(config_dict=config_dict)
        pass


    @staticmethod
    def from_dict(origin_request_config_dict: dict):
        request_config_dict = {
            # 'request_type': 'browser_chrome_single_tab'
        }

        # 1. 获取请求类型, 如果没有则抛出异常
        if origin_request_config_dict.get("request_type"):
            request_type = RequestType(origin_request_config_dict.get("request_type"))
            request_config_dict.update({'request_type': request_type})
        else:
            raise ValueError("请求类型不能为空")

        # todo: 2. 判断 request_type 是否是 website 的

        return WebsiteTaskRequestConfig(config_dict=request_config_dict)


    def to_dict(self) -> dict:
        """
        转 dict, 用于保存到文件
        :return:
        """
        request_config_dict = {}
        request_config_dict.update({'request_type': self.config_dict.get("request_type").value})

        return request_config_dict