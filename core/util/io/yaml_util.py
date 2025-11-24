__doc__ = "YAML读写工具类"
__author__ = "Li Qingyun"
__date__ = "2025-02-26"

from threading import Lock

import yaml
from ruamel.yaml import YAML, CommentedMap

from core.util.python.singleton_util import Singleton


@Singleton  # 单例模式
class YamlUtil:
    """
    YAML 工具类
    """

    def __init__(self):
        # 乐观锁, 写时获取
        self._lock = Lock()

        self._write_yaml = YAML()
        self._write_yaml.indent(mapping=2, sequence=4, offset=2)
        self._write_yaml.allow_unicode = True     # 正常保存中文

        self._read_yaml = YAML(typ='safe')
        pass

    def load(self, file_path):
        """
        读取yaml
        :param file_path:
        :return:
        """
        with open(file_path, 'r', encoding='utf-8') as file_path:
           data = yaml.safe_load(file_path)
        return data

    def load_with_comments(self, file):
        with open(file, 'r', encoding='utf-8') as file:
           data = self._read_yaml.load(file)
        return data


    def dump(self, data, file_path):
        """
        普通保存
        :param data:
        :param file_path:
        :return:
        """
        with self._lock:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)


    def dump_with_comments(self, commented_yaml_data, file_path):
        """
        保存含有comments的yaml
        :param commented_yaml_data:
        :param file_path:
        :return:
        """
        with self._lock:
            with open(file_path, 'w', encoding='utf-8') as file:
                self._write_yaml.dump(commented_yaml_data, file)


    def add_comments_before(self, data, comments_dict):
        """
        在数据前加注释
        :param data:
        :param comments_dict:
        :return:
        """
        commented_data = CommentedMap(data)
        for key in comments_dict.keys():
            if key not in commented_data:
                continue
            commented_data.yaml_set_comment_before_after_key(key, before=comments_dict.get(key))
        return commented_data


    def add_comments_after(self, data, comments_dict):
        """
        在字段后加注释
        :param data:
        :param comments_dict:
        :return:
        """
        commented_data = CommentedMap(data)
        for key, comment in comments_dict:
            commented_data.yaml_set_comment_before_after_key(0, before=comment)
        return commented_data


    def add_cycle_comments(self, data, comments_dict):
        """
        循环将 comments_dict 中的注释添加到 data 的对应层级上。

        :param data: 目标字典（可以是普通字典或 CommentedMap）。
        :param comments_dict: 包含注释的字典，结构与 data 相同。
        :return: 添加注释后的字典（CommentedMap）。
        """
        if not isinstance(data, CommentedMap):
            data = CommentedMap(data)  # 将普通字典转换为 CommentedMap


        for key, value in comments_dict.items():
            if key == 'main_comment':
                # 添加主注释
                data.yaml_set_start_comment(value)
            elif key in data:
                if isinstance(value, dict) and isinstance(data[key], dict):
                    # 递归处理嵌套字典
                    data[key] = self.add_cycle_comments(data[key], value)
                elif isinstance(value, str):
                    # 添加键值对注释
                    data.yaml_set_comment_before_after_key(key, before=value)
                    # data.yaml_add_eol_comment(value, key)
                else:
                    return
            else:
                # key 不在 data 里, 跳过
                pass

        return data