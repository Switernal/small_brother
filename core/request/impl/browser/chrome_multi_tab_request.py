__doc__ = "Chrome多标签请求线程"
__author__ = "Li Qingyun"
__date__ = "2025-03-09"

from time import sleep

import psutil
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from core.request.const.request_type import RequestType
from core.request.interface.request_thread import RequestThread
from core.util.io.log_util import LogUtil
from core.util.io.path_util import PathUtil
from core.util.string.time_util import TimeUtil
from core.util.string.url_util import UrlUtil


class ChromeMultiTabRequest(RequestThread):


    def __init__(self,
                 task_name,
                 request_name: str,
                 urls: dict[str],
                 interval: int=0,           # 默认无间隔
                 screenshots_dir=None,
                 timeout=None,
                 use_proxy=False,
                 proxy_port=None
                 ):
        """

        :param urls:                要抓取的多标签url列表
        :param interval:            每个页面之间打开间隔
        :param screenshots_dir:     截图保存路径
        :param timeout:             加载超时时间
        :param use_proxy:           是否使用代理
        :param proxy_port:          代理端口
        """
        super().__init__(task_name=task_name, request_name=request_name)

        # 加载策略
        #   1. 要加载的url
        self.urls = urls
        #   2. 加载间隔
        self.interval = interval
        #   3. 截图保存路径
        self.screenshots_dir = screenshots_dir
        #   4. 超时时间
        #       如果timeout为None, 就默认加载到网页结束
        #       如果不是None, 就在启动后sleep(self.timeout), 到点停止
        self.timeout = timeout

        # 代理参数配置
        self.use_proxy = use_proxy      # 是否使用代理
        self.proxy_port = proxy_port    # 如果使用代理, 设置代理端口

        # 浏览器相关配置
        self.options = Options()
        self.web_driver = None
        self.network_service_pid = None     # Chrome Network Service 进程的 PID


    def run(self):
        self.send_request()
        self.end_request()


    def create_request(self):
        self._create_and_initial_web_driver()
        pass

    def send_request(self):
        # 1. 访问网页并获取加载结果
        result = self._visit_urls()
        # 2. 如果加载成功, 就保存截图
        if result is True:
            self._save_screenshots()
        pass

    def end_request(self):
        # 关闭浏览器
        self._stop_web_driver()
        pass

    def clear(self):
        # 没有需要清理的东西
        pass


    # ----- 浏览器设置 -----
    def __setup_proxy_option(self):
        """配置浏览器代理设置"""
        LogUtil().debug(self.request_name, f'浏览器的代理端口: {self.proxy_port}')
        if self.use_proxy is True and self.proxy_port is not None:
            self.options.add_argument(f"--proxy-server=http://127.0.0.1:{self.proxy_port}")


    def __find_chrome_network_service_pid(self):
        """
        通过 Selenium 的 Chrome WebDriver 实例查找 Network Service 进程的 PID
        :return: Network Service 进程的 PID（若未找到返回 None）
        """
        # 获取 WebDriver 进程 PID（通常是 chromedriver）
        chromedriver_pid = self.web_driver.service.process.pid

        # 查找 chromedriver 的子进程（即 Chrome 主进程）
        chrome_main_pid = None
        for proc in psutil.process_iter(['pid', 'ppid', 'name', 'cmdline']):
            if proc.ppid() == chromedriver_pid and 'Google Chrome' in ' '.join(proc.cmdline()):
                chrome_main_pid = proc.pid
                break

        if not chrome_main_pid:
            LogUtil().debug(self.request_name, "[BrowserRunner] 未找到 Chrome 主进程")
            return None

        # 递归查找 Chrome 主进程的所有子进程
        def find_children(pid):
            children = []
            for _proc in psutil.process_iter(['pid', 'ppid', 'cmdline']):
                if _proc.ppid() == pid:
                    children.append(_proc)
                    children.extend(find_children(_proc.pid))
            return children

        all_children = find_children(chrome_main_pid)

        # 筛选 Network Service 进程
        # 注: Chrome会把所有网络连接交给Network Service进程处理, 只需要抓这个进程即可
        for proc in all_children:
            cmdline = ' '.join(proc.cmdline())
            if '--utility-sub-type=network.mojom.NetworkService' in cmdline:
                self.network_service_pid = proc.pid
                break

        return self.network_service_pid


    # ----- 浏览器操作 -----
    def _create_and_initial_web_driver(self):
        """
        创建并初始化浏览器
        :return:
        """
        self.options.add_argument("--headless")                         # 无头模式
        self.options.add_argument("--no-sandbox")                       # 禁用沙盒（Linux 必需）
        # self.options.add_argument("--disable-dev-shm-usage")          # 避免 /dev/shm 内存不足
        self.options.add_argument("--disable-gpu")                      # 禁用 GPU 硬件加速
        # self.options.add_argument("--remote-debugging-port=9222")     # 固定调试端口
        self.options.add_argument("--dns-prefetch-disable")             # 禁用DNS预取
        self.options.add_argument(                                      # UA标识
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # 设置浏览器代理Option
        self.__setup_proxy_option()

        self.web_driver = webdriver.Chrome(options=self.options)

        # 反爬虫 JS
        self.web_driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                    })
                    """
            },
        )
        # 获取 Chrome Network Service 进程的 PID
        self.__find_chrome_network_service_pid()


    async def __open_new_tab(self, url, delay):
        """
        打开指定 URL 的标签页
        :param url: 要打开的网页 URL
        :param delay: 绝对延迟时间（秒）
        """
        await asyncio.sleep(delay)                                  # 等待指定时间
        self.web_driver.execute_script(f"window.open('{url}')")     # 打开新标签页
        window_handles = self.web_driver.window_handles
        self.web_driver.switch_to.window(window_handles[-1])        # 切换到新标签页
        # LogUtil().debug(self.request_name, f"已打开: {url}, 标题: {self.web_driver.title}")


    async def _visit_urls(self) -> bool:
        """
        访问网页并等待加载完成
        :return: bool: 加载成功与否
        """
        # 设置超时策略, 如果没有超时默认阻塞加载到结束
        if self.timeout is not None and self.timeout > 0:
            self.web_driver.set_script_timeout(self.timeout)

        for i, url in enumerate(self.urls):
            try:
                LogUtil().debug(self.request_name, f'[BrowserRunner] 第 {i} 个网页 {url} 开始加载')
                await self.__open_new_tab(url, i * self.interval)    # 第 i 个网页等待 i * interval 秒
            except Exception as e:
                LogUtil().debug(self.request_name, f'[BrowserRunner] 第 {i} 个网页 {url} 加载出错, 错误: {e}')
                return False

        return True


    def _save_screenshots(self):
        """保存网页截图"""
        if self.screenshots_dir is None:
            return

        # 窗口管理器
        window_handles = self.web_driver.window_handles

        # 设置浏览器窗口大小分辨率, 决定了截图大小和加载内容(桌面端/手机端)
        # self.web_driver.set_window_size(1280, 960)               # 清晰度太高,可能截图文件过大
        self.web_driver.set_window_size(1024, 768)
        # self.web_driver.set_window_size(960, 540)
        # self.web_driver.set_window_size(800, 600)

        # 时间戳
        now_time_str = TimeUtil.now_time_str()

        screenshot_names = []
        for i, url in enumerate(self.urls):
            self.web_driver.switch_to.window(window_handles[i])  # 切换到第 i 个标签页
            url_for_dir = UrlUtil.get_main_domain(url)
            screenshot_name = f'screenshot_{i}_{url_for_dir}_{now_time_str}.png'
            screenshot_file_path = PathUtil.file_path_join(self.screenshots_dir, file_path=screenshot_name)
            self.web_driver.save_screenshot(screenshot_file_path)
            screenshot_names.append(screenshot_name)
            sleep(0.5)

        LogUtil().debug(self.request_name, f'[BrowserRunner] {len(self.urls)} 个网页截图保存成功: {screenshot_names}')


    def _stop_web_driver(self):
        """
        关闭浏览器实例
        """
        LogUtil().debug(self.request_name, "[BrowserRunner] 关闭浏览器")
        if self.web_driver:
            self.web_driver.quit()


    def get_request_thread_info(self):
        return {
            'request_type': RequestType.BROWSER_CHROME_MULTI_TAB,
            'pid': self.network_service_pid
        }



    @staticmethod
    def create_request_thread_by_config(task_name, request_name: str, config: dict):
        return ChromeMultiTabRequest(
            task_name=task_name,
            request_name=request_name,
            urls=config.get('urls'),
            screenshots_dir=config.get('screenshot_dir'),
            timeout=config.get('timeout'),
            use_proxy=config.get('use_proxy'),
            proxy_port=config.get('proxy_port'),
        )
        pass