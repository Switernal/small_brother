__doc__="单标签网页任务配置"
__author__="Li Qingyun"
__date__="2025-03-10"

from core.task.const.task_type import TaskType
from core.task.interface.task_config.task_capture_context import TaskCaptureContext
from core.task.interface.task_config.task_capture_policy import TaskCapturePolicy
from core.task.interface.task_config.task_config import TaskConfig
from core.util.io.yaml_util import YamlUtil
from core.task.impl.website.task_config.website_task_extension_config import WebsiteTaskExtensionConfig
from core.task.impl.website.task_config.website_task_preference import WebsiteTaskPreference
from core.task.impl.website.task_config.website_task_request_config import WebsiteTaskRequestConfig


class WebsiteSingleTabTaskConfig(TaskConfig):

    def __init__(self,
                 task_name: str,
                 task_note: str,
                 task_type: TaskType,
                 output_dir: str,
                 extension_config: WebsiteTaskExtensionConfig,
                 request_config: WebsiteTaskRequestConfig,
                 capture_policy: TaskCapturePolicy,
                 capture_context: TaskCaptureContext,
                 preference: WebsiteTaskPreference,
                 website_list_path: str,
                 ):
        super().__init__(
            task_name=task_name,
            task_note=task_note,
            task_type=task_type,
            output_dir=output_dir,
            extension_config=extension_config,
            request_config=request_config,
            capture_policy=capture_policy,
            capture_context=capture_context,
            preference=preference
        )
        # 网站列表文件路径
        self.website_list_path = website_list_path
        pass


    @staticmethod
    def create_task_config_from_file(config_file_path: str):
        """
        根据配置文件创建任务配置类
        :param config_file_path: 配置文件路径
        :return: WebsiteSingleTabTaskConfig 对象
        """
        # 读取文件内容
        config_content = YamlUtil().load(config_file_path)
        # 解析文件
        # 1. 任务名
        if config_content.get('task_name'):
            task_name = config_content.get('task_name')
        else:
            raise ValueError('[WebsiteSingleTabTaskConfig] 任务名称不能为空')

        # 2. 任务备注
        if config_content.get('task_note'):
            task_note = config_content.get('task_note')
        else:
            raise ValueError('[WebsiteSingleTabTaskConfig] 任务备注不能为空')

        # 3. 任务类型
        if config_content.get('task_type'):
            task_type = TaskType(config_content.get('task_type'))
        else:
            raise ValueError('[WebsiteSingleTabTaskConfig] 任务类型不能为空')

        # 4. 网站列表
        if config_content.get('website_list_path'):
            website_list_path = config_content.get('website_list_path')
        else:
            raise ValueError('[WebsiteSingleTabTaskConfig] 网站列表不能为空')

        # 5. 输出目录
        if config_content.get('output_dir'):
            output_dir = config_content.get('output_dir', '.')
        else:
            raise ValueError('[WebsiteSingleTabTaskConfig] 输出目录不能为空')

        # 6. 扩展配置
        if config_content.get('extension_config'):
            extension_config = WebsiteTaskExtensionConfig.from_dict(config_content.get('extension_config'))
        else:
            extension_config = None

        # 7. request 配置
        if config_content.get('request_config'):
            request_config = WebsiteTaskRequestConfig.from_dict(config_content.get('request_config'))
        else:
            request_config = None

        # 8. 抓取策略
        if config_content.get('capture_policy'):
            capture_policy = TaskCapturePolicy.from_dict(config_content.get('capture_policy'))
        else:
            raise ValueError('[WebsiteSingleTabTaskConfig] 抓取策略不能为空')

        # 9. 上下文
        if config_content.get('capture_context'):
            capture_context = TaskCaptureContext.from_dict(config_content.get('capture_context'))
        else:
            raise ValueError('[WebsiteSingleTabTaskConfig] 上下文不能为空')

        # 10. 偏好
        preference = WebsiteTaskPreference.from_dict(config_content.get('preference', {}))



        return WebsiteSingleTabTaskConfig(
            task_name=task_name,
            task_note=task_note,
            task_type=task_type,
            website_list_path=website_list_path,
            output_dir=output_dir,
            extension_config=extension_config,
            request_config=request_config,
            capture_policy=capture_policy,
            capture_context=capture_context,
            preference=preference,
        )


    def convert_to_yaml_data(self) -> dict:
        """
        转换成yaml dict数据
        :return:
        """
        yaml_data = {}
        yaml_data.update({'task_name': self.task_name})
        yaml_data.update({'task_note': self.task_note})
        yaml_data.update({'task_type': self.task_type.value})
        yaml_data.update({'website_list_path': self.website_list_path})
        yaml_data.update({'output_dir': self.output_dir})
        yaml_data.update({'capture_policy': self.capture_policy.to_dict()})
        yaml_data.update({'capture_context': self.capture_context.to_dict()})
        yaml_data.update({'preference': self.preference.to_dict()})

        if self.extension_config is not None and len(self.extension_config.config_dict.keys()) > 0:
            yaml_data.update({'extension_config': self.extension_config.to_dict()})

        if self.request_config is not None and len(self.request_config.config_dict.keys()) > 0:
            yaml_data.update({'request_config': self.request_config.to_dict()})
        return yaml_data


    def convert_to_commented_yaml_data(self):
        """
        转成带注释的yaml数据
        :return:
        """
        yaml_commented_data = YamlUtil().add_cycle_comments(
            self.convert_to_yaml_data(),
            self.comments_for_yaml_data()
        )

        return yaml_commented_data


    def comments_for_yaml_data(self):
        """给yaml数据添加注释"""
        return {
            'task_name': '任务名称',
            'task_note': '任务备注',
            'website_list_path': '网站列表文件路径',
            'output_dir': '输出主目录',
            'extension_config': '扩展配置',
            'request_config': '请求配置',
            'capture_policy': self.capture_policy.comments_for_yaml_data().get('main_comment'),
            'task_context': self.capture_context.comments_for_yaml_data().get('main_comment'),
            'preference': self.preference.comments_for_yaml_data().get('main_comment')
        }
