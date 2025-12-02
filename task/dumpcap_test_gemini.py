import subprocess
import socket
import os
import sys
import signal
import time

# ================= 配置区域 =================
TARGET_HOST = "seu.switernal.com"
TARGET_PORT = "9300"
OUTPUT_FILE = "C:\\capture.pcapng"  # 你可以修改保存路径
BUFFER_SIZE = "200"  # 200MB 缓冲区


# ===========================================

def find_dumpcap():
    """寻找 Windows 下的 dumpcap.exe"""
    possible_paths = [
        r"C:\Program Files\Wireshark\dumpcap.exe",
        r"C:\Program Files (x86)\Wireshark\dumpcap.exe",
    ]

    # 先检查环境变量
    try:
        subprocess.run(["dumpcap", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "dumpcap"
    except FileNotFoundError:
        pass

    # 检查默认路径
    for path in possible_paths:
        if os.path.exists(path):
            return path

    print("❌ 错误: 未找到 dumpcap.exe。请确认已安装 Wireshark 并将其添加到 PATH，或修改脚本中的路径。")
    sys.exit(1)


def resolve_ips(domain):
    """解析域名下的所有 IP，生成过滤规则"""
    print(f"🔍 正在解析域名: {domain} ...")
    try:
        # 获取该域名的所有 IP 地址 (IPv4)
        _, _, ip_list = socket.gethostbyname_ex(domain)
        print(f"✅ 解析成功，发现 IP: {ip_list}")

        # 构建 BPF 过滤器字符串
        # 格式: (host 1.1.1.1 or host 2.2.2.2)
        ip_filters = " or ".join([f"host {ip}" for ip in ip_list])
        final_filter = f"({ip_filters}) and port {TARGET_PORT}"
        return final_filter
    except socket.gaierror:
        print(f"❌ 错误: 无法解析域名 {domain}，请检查网络。")
        sys.exit(1)


def select_interface(dumpcap_path):
    """列出网卡并让用户选择"""
    print("\n📋 正在读取网卡列表...\n")
    result = subprocess.run([dumpcap_path, "-D"], capture_output=True, text=True)
    interfaces = result.stdout.strip().split('\n')

    for line in interfaces:
        print(line)

    choice = input("\n👉 请输入你要抓包的网卡序号 (例如 1): ").strip()
    if not choice.isdigit():
        print("❌ 输入无效，请输入数字。")
        sys.exit(1)
    return choice


def main():
    dumpcap_path = find_dumpcap()

    # 1. 选择网卡
    interface_id = select_interface(dumpcap_path)

    # 2. 解析域名生成更稳健的过滤器
    bpf_filter = resolve_ips(TARGET_HOST)
    print(f"\n🛡️  生成的抓包过滤器: \"{bpf_filter}\"")

    # 3. 构建命令
    # -i: 网卡
    # -f: 过滤器
    # -w: 写入文件
    # -B: 缓冲区大小 (MB)
    cmd = [
        dumpcap_path,
        "-i", interface_id,
        "-f", bpf_filter,
        "-w", OUTPUT_FILE,
        "-B", BUFFER_SIZE
    ]

    print(f"\n🚀 开始抓包！数据将保存到: {OUTPUT_FILE}")
    print("🛑 按 Ctrl+C 停止抓包...\n")
    print("-" * 50)

    try:
        # 启动子进程
        process = subprocess.Popen(cmd)
        process.wait()  # 等待进程结束
    except KeyboardInterrupt:
        print("\n\n🛑 用户终止操作。正在停止 dumpcap...")
        # 此时 dumpcap 通常会收到信号并优雅退出，但为了保险：
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        print("✅ 抓包结束。")


if __name__ == "__main__":
    main()