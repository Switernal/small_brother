import locale
import re
import shutil
import subprocess

# 如果你知道 dumpcap 的绝对路径，可以直接写死在这里，例如：
# DUMPCAP_PATH = r"C:\Program Files\Wireshark\dumpcap.exe"
# 不写就自动用 PATH 里的 dumpcap
DUMPCAP_PATH = None


class DumpcapUtil:

    @staticmethod
    def get_dumpcap_cmd():
        """
        返回 dumpcap 的启动命令（列表形式），优先使用绝对路径，其次使用 PATH。
        """
        if DUMPCAP_PATH and DUMPCAP_PATH != "":
            return [DUMPCAP_PATH]

        found = shutil.which("dumpcap")
        if found:
            return [found]

        raise FileNotFoundError(
            "未找到 dumpcap 可执行文件，请确认：\n"
            "1) 已安装 Wireshark（包含 dumpcap）\n"
            "2) dumpcap.exe 在环境变量 PATH 中，或者在脚本中设置 DUMPCAP_PATH"
        )

    @staticmethod
    def get_network_interface_id_by_name(network_interface_name: str):
        """
        根据网卡名称获取网络接口id, 用于启动指令参数
        """
        interface_lines = DumpcapUtil._get_dumpcap_interfaces()
        return DumpcapUtil._find_interface_index_by_name(
            target_name=network_interface_name,
            interfaces_lines=interface_lines
        )


    """
    以下为私有方法
    """

    @staticmethod
    def _safe_decode_output(output_bytes: bytes) -> str:
        """
        尝试用多种编码解码 dumpcap 输出，避免 UnicodeDecodeError。
        优先 utf-8，其次系统默认编码/gbk，最后 ignore 非法字符。
        """
        enc_candidates = [
            "utf-8",
            locale.getpreferredencoding(False) or "gbk",
            "gbk",
        ]

        for enc in enc_candidates:
            try:
                return output_bytes.decode(enc)
            except UnicodeDecodeError:
                continue

        return output_bytes.decode(errors="ignore")

    @staticmethod
    def _get_dumpcap_interfaces():
        """
        调用 `dumpcap -D` 获取接口列表，按行返回。
        用二进制方式读出，再手动解码。
        """
        cmd = DumpcapUtil.get_dumpcap_cmd() + ["-D"]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,  # 不自动解码
                check=False,
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"执行 {' '.join(cmd)} 失败，系统找不到 dumpcap。\n"
                f"请检查 Wireshark 是否安装，或者设置 DUMPCAP_PATH。"
            ) from e

        output = DumpcapUtil._safe_decode_output(result.stdout)

        if result.returncode != 0:
            raise RuntimeError(f"执行 'dumpcap -D' 失败：\n{output}")

        return output.splitlines()

    @staticmethod
    def _find_interface_index_by_name(target_name, interfaces_lines):
        """
        根据接口名称（或其子串）找到对应的接口编号。
        dumpcap -D 输出通常类似：
            1. Ethernet
            2. 以太网 2
            3. \Device\NPF_{GUID} (以太网 2)
        只要行里包含 target_name 就认为匹配。
        """
        for line in interfaces_lines:
            m = re.match(r"\s*(\d+)\.\s*(.*)", line)
            if not m:
                continue

            idx = int(m.group(1))
            desc = m.group(2)

            if target_name in desc:
                return idx

        raise ValueError(f"未找到名称包含 '{target_name}' 的接口，请检查网卡名字或 dumpcap -D 输出。")