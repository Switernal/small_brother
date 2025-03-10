__doc__ = "路径工具类"
__author__ = "Li Qingyun"
__date__ = "2025-02-26"

import os


class PathUtil:
    @staticmethod
    def auto_create_path(path: str) -> None:
        """
        自动创建路径
        :param path: 路径
        """
        if not os.path.exists(path):
            os.makedirs(path)


    @staticmethod
    def dir_path_join(a: str, *paths: [str]):
        """
        拼接目录路径
        """
        # 生成新的目录路径
        new_path = a
        for path in paths:
            new_path = os.path.join(new_path, path)
        PathUtil.auto_create_path(str(new_path))
        return new_path


    @staticmethod
    def file_path_join(*paths: [str], file_path: str):
        """
        拼接文件路径
        """
        # 先生成目录路径
        dir_path = ''
        for path in paths:
            dir_path = os.path.join(dir_path, path)
        PathUtil.auto_create_path(str(dir_path))

        new_file_path = os.path.join(str(dir_path), file_path)
        return new_file_path