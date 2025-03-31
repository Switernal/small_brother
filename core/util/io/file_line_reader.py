__doc__ = "文件行读取器"
__author__ = "Li Qingyun"
__date__ = "2025-02-28"


class FileLineReader:
    """
    按行读取文件的读取器, 可以指定读取到某一行
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self._file = open(file_path, 'rb')
        self.offsets = []
        self._build_index()
        self.current_line = 0


    def _build_index(self):
        """
        构建索引
        :return:
        """
        self._file.seek(0)
        while True:
            offset = self._file.tell()
            line = self._file.readline()
            if not line:
                break
            self.offsets.append(offset)
        self._file.seek(0)

    def seek_to_line(self, line_number):
        """
        获取到指定行
        :param line_number: 行号
        :return:
        """
        if line_number < 0 or line_number >= len(self.offsets):
            raise ValueError(f"[FileLineReader] 行号必须在 0 到 {self.get_total_line_num() - 1}(总行数-1) 之间")
        self._file.seek(self.offsets[line_number])
        self.current_line = line_number

    def read_line(self):
        """
        读取下一行
        :return: 下一行内容
        """
        line = self._file.readline()
        if not line:
            return None
        return line.decode('utf-8').rstrip('\r\n')

    def move_next_line(self):
        """
        指针移到下一行
        :return:
        """
        self.current_line += 1


    def get_current_line_num(self):
        """
        获取当前行号
        :return:
        """
        return self.current_line


    def get_total_line_num(self):
        """
        总行数
        :return:
        """
        return len(self.offsets)


    def __enter__(self):
        """
        进入上下文
        :return:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self._file.close()

    def close(self):
        """
        关闭文件
        :return:
        """
        self._file.close()


    def is_finish(self):
        """
        是否完成
        :return: bool
        """
        if self.current_line >= self.get_total_line_num():
            return True
        else:
            return False


    def __del__(self):
        self._file.close()