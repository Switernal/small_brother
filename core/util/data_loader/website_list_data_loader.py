__doc__ = "网站列表数据加载器"
__author__ = "Li Qingyun"
__date__ = "2025-02-27"

from core.util.io.file_line_reader import FileLineReader


class WebsiteListDataLoader(FileLineReader):
    """
    读取和控制网站列表文件的数据加载器
        实现了LineReader接口
    """
    def __init__(self, file_path):
        """
        构造函数
        :param file_path: 网站列表数据文件路径
        """
        super().__init__(file_path)
        self._file = open(self.file_path, 'rb')
        self.offsets = []
        self._build_index()
        self.current_line = 0
        pass


    def __load_all_data(self):
        """
        读取全部数据(不推荐使用)
        :return: 网站列表
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            websites = f.readlines()
            websites = [website.strip() for website in websites]
            return websites
        pass