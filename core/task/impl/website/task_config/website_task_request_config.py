__doc__='网站请求配置'
__author__='Li Qingyun'
__date__='2025-03-10'

from core.request.const.request_type import RequestType
from core.task.interface.task_config.task_request_config import TaskRequestConfig


class WebsiteTaskRequestConfig(TaskRequestConfig):

    def __init__(self,
                 config_dict: dict,
                 ):
        super().__init__(config_dict=config_dict)
        pass


    @staticmethod
    def from_dict(origin_request_config_dict: dict):
        request_config_dict = {
            # 'request_type': 'browser_chrome_single_tab'
        }

        # 1. 请求类型
        if origin_request_config_dict.get("request_type"):
            request_type = RequestType(origin_request_config_dict.get("request_type"))
            request_config_dict.update({'request_type': request_type})
        else:
            raise ValueError("请求类型不能为空")

        return WebsiteTaskRequestConfig(config_dict=request_config_dict)


    def to_dict(self) -> dict:
        request_config_dict = {}
        request_config_dict.update({'request_type': self.config_dict.get("request_type").value})

        return request_config_dict