import shutil

# 如果你知道 tcpdump 的绝对路径，可以直接写死在这里，例如：
# TCPDUMP_PATH = r"/etc/tcpdump"
# 不写就自动用 PATH 里的 tcpdump
TCPDUMP_PATH = None


class TcpdumpUtil:

    @staticmethod
    def get_tcpdump_cmd():
        """
        返回 tcpdump 的启动命令（列表形式），优先使用绝对路径，其次使用 PATH。
        """
        if TCPDUMP_PATH and TCPDUMP_PATH != "":
            return [TCPDUMP_PATH]

        found = shutil.which("tcpdump")
        if found:
            return [found]

        raise FileNotFoundError(
            "未找到 tcpdump 可执行文件，请确认：\n"
            "1) tcpdump 在环境变量 PATH 中，或者在脚本中设置 TCPDUMP_PATH"
        )
