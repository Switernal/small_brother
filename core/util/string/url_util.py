__doc__='URL工具类'
__author__='Li Qingyun'
__date__='2025-03-09'


class UrlUtil():

    @staticmethod
    def get_main_domain(url: str) -> str:
        """
        获取URL的域名部分

            例: https://apple.com/zh-cn -> apple.com

        :return: 主域名部分
        """
        return url.split("//")[-1].split("/")[0].split("?")[0]

