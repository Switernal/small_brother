__doc__ = "Chrome单标签请求线程"
__author__ = "Li Qingyun"
__date__ = "2025-02-27"

import os
import platform
from time import sleep
import time

import psutil
from psutil import AccessDenied, NoSuchProcess
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from core.request.const.request_type import RequestType
from core.request.interface.request_thread import RequestThread
from core.util.io.log_util import LogUtil
from core.util.io.path_util import PathUtil
from core.util.string.time_util import TimeUtil
from core.util.string.url_util import UrlUtil


class ChromeSingleTabRequest(RequestThread):

    def __init__(self,
                 task_name,
                 request_name,
                 url,
                 screenshot_dir=None,
                 screenshot_name=None,
                 timeout=None,
                 wait_element_id=None,
                 use_proxy=False,
                 proxy_port=None
                 ):
        """
        单标签浏览器请求
        :param url:                 要抓取的url
        :param screenshot_dir:      截图保存路径
        :param screenshot_name:     截图命名
        :param timeout:             加载超时时间
        :param wait_element_id:     加载完成的标志元素id
        :param use_proxy:           是否使用代理
        :param proxy_port:          代理端口
        """
        super().__init__(task_name=task_name, request_name=request_name)

        # 加载策略
        #   1. 要加载的url
        self.url = url
        #   2. 截图保存路径
        self.screenshot_dir = screenshot_dir
        #   3. 截图文件名
        self.screenshot_name = screenshot_name
        #   4. 超时时间
        #       如果timeout为None, 就默认加载到网页结束
        #       如果不是None, 就在启动后sleep(self.timeout), 到点停止
        self.timeout = timeout
        #   5. 等待元素: 加载完成的标志元素, 如果指定元素出现就认为加载结束, 默认为空
        self.wait_element_id = wait_element_id

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
        result = self._visit_url()
        # 2. 如果加载成功, 就保存截图
        if result is True:
            self._save_screenshot()
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
        LogUtil().debug(self.task_name, f'浏览器的代理端口: {self.proxy_port}')
        if self.use_proxy is True and self.proxy_port is not None:
            self.options.add_argument(f"--proxy-server=http://127.0.0.1:{self.proxy_port}")

    def __find_chrome_network_service_pid(self):
        """
        通过 Selenium 的 Chrome WebDriver 实例查找 Network Service 进程的 PID
        优化版：不再遍历全系统进程，直接利用父子进程关系查找
        """
        self.network_service_pid = None

        # 1. 获取 chromedriver 进程对象
        try:
            chromedriver_pid = self.web_driver.service.process.pid
            driver_process = psutil.Process(chromedriver_pid)
        except psutil.NoSuchProcess:
            LogUtil().debug(self.task_name, "[BrowserRunner] Chromedriver 进程已不存在")
            return None

        # 2. 查找 Chrome 主进程 (Chromedriver 的直接子进程)
        chrome_main_proc = None

        # 重试机制：有时候 Chrome 启动稍慢，刚开始 driver 下面可能还没挂上子进程
        for _ in range(5):
            try:
                children = driver_process.children(recursive=False)  # 只找亲儿子
                if children:
                    # 通常 Chromedriver 只有一个子进程就是 Chrome 浏览器主进程
                    chrome_main_proc = children[0]
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            time.sleep(0.5)

        if not chrome_main_proc:
            LogUtil().debug(self.task_name, "[BrowserRunner] 未能找到 Chrome 主进程")
            return None

        LogUtil().debug(self.task_name, f"[BrowserRunner] 找到 Chrome 主进程ID: {chrome_main_proc.pid}")

        # 3. 查找 Network Service 进程 (Chrome 主进程的后代)
        try:
            # 关键优化：recursive=True 一次性获取所有后代，不需要自己写递归，也不需要扫描全系统
            all_descendants = chrome_main_proc.children(recursive=True)

            target_flag = '--utility-sub-type=network.mojom.NetworkService'

            for proc in all_descendants:
                try:
                    # 获取命令行参数 (cmdline返回的是list)
                    cmdline = proc.cmdline()
                    # 检查参数列表中是否包含目标 flag
                    # 注意：cmdline 是 list，需要判断 element 是否包含字符串，或者 join 后判断
                    if any(target_flag in arg for arg in cmdline):
                        self.network_service_pid = proc.pid
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except psutil.NoSuchProcess:
            LogUtil().debug(self.task_name, "[BrowserRunner] Chrome 主进程在查找过程中消失")

        if self.network_service_pid:
            LogUtil().warning(self.task_name,
                              f"[BrowserRunner] Chrome Network Service 进程ID: {self.network_service_pid}")
        else:
            LogUtil().warning(self.task_name, "[BrowserRunner] 未找到 Network Service 进程")

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
        self.options.add_argument('--enable-unsafe-swiftshader')        # 启用 SwiftShader，这是一种基于软件的图形渲染器，防止硬件加速问题
        self.options.add_argument(                                      # UA标识
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # 设置浏览器代理Option
        self.__setup_proxy_option()

        try:
            # 强制安装适配当前系统的驱动
            # 这会自动区分 mac-arm64 (M芯片) 和 mac-x64
            # driver_path = ChromeDriverManager().install()
            #
            # service = Service(driver_path)
            # 关键调试：打印一下它到底下载了哪个版本，方便排查
            # print(f"Loading ChromeDriver from: {driver_path}")
            # 重新初始化
            # self.web_driver = webdriver.Chrome(service=service, options=self.options)

            self.web_driver = webdriver.Chrome(options=self.options)

        except Exception as e:
            print("启动失败，请检查下方报错与路径")
            # 如果依然报错，这个 print 能救命
            import traceback
            traceback.print_exc()
            raise e

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

        # 设置页面加载的硬性超时时间
        # 即使 strategy 是 eager，有时候 DOM 也会卡住。
        # 这里建议设置一个上限，比如 30秒，或者用你传入的 timeout (如果 timeout 比较大的话)
        # 这里我写死 30秒作为兜底，防止无限卡死
        self.web_driver.set_page_load_timeout(self.timeout)

        # 获取 Chrome Network Service 进程的 PID
        self.__find_chrome_network_service_pid()


    def _visit_url(self) -> bool:
        """
        访问网页并等待加载完成
        :return: bool: 加载成功与否
        """
        LogUtil().debug(self.task_name, f'[BrowserRunner] 网页 {self.url} 开始加载')

        try:
            # 尝试访问
            self.web_driver.get(self.url)
        except TimeoutException:
            # 【关键修改】如果加载超时（超过了 set_page_load_timeout 设置的时间）
            # 我们手动发送停止指令，强行让浏览器认为加载结束，然后继续往下走去截图
            LogUtil().debug(self.task_name, f'[BrowserRunner] 网页 {self.url} 触发硬性加载超时，强制停止加载继续执行')
            try:
                self.web_driver.execute_script("window.stop();")
            except Exception:
                pass
        except Exception as e:
            LogUtil().debug(self.task_name, f'[BrowserRunner] 网页 {self.url} 加载发生未知错误: {e}')
            return False

        try:
            if self.timeout is not None and self.timeout > 0:
                sleep(self.timeout)
                pass

                # 如果你有特定的元素要等，可以在这里等
                # 但因为前面已经是 eager 模式，DOM 大概率都在了
            if self.wait_element_id is not None:
                try:
                    WebDriverWait(self.web_driver, 5).until(  # 建议这里 wait 时间短一点
                        lambda d: d.find_element(*self.wait_element_id)
                    )
                except TimeoutException:
                    LogUtil().debug(self.task_name, f'[BrowserRunner] 等待特定元素超时，忽略并继续截图')
            else:
                WebDriverWait(self.web_driver, self.timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
        except Exception as e:
            LogUtil().debug(self.task_name, f'[BrowserRunner] 网页 {self.url} 加载出错, 错误: {e}')
            return False
        finally:
            LogUtil().debug(self.task_name, f'[BrowserRunner] 网页 {self.url} 加载完成')

        return True


    def _save_screenshot(self):
        """保存网页截图"""
        if self.screenshot_dir is None:
            # 如果没有提供目录, 默认就不保存了
            return

        # 设置浏览器窗口大小分辨率, 决定了截图大小和加载内容(桌面端/手机端)
        self.web_driver.set_window_size(1280, 960)               # 清晰度太高,可能截图文件过大
        # self.web_driver.set_window_size(1024, 768)
        # self.web_driver.set_window_size(960, 540)
        # self.web_driver.set_window_size(800, 600)

        if self.screenshot_name is None:
            # 如果没有提供名字, 采用默认命名
            url_for_dir = UrlUtil.get_main_domain(self.url)
            self.screenshot_name = f'screenshot_{url_for_dir}_{TimeUtil.now_time_str()}.png'

        screenshot_file_path = PathUtil.file_path_join(self.screenshot_dir, file_path=self.screenshot_name)

        try:
            self.web_driver.save_screenshot(screenshot_file_path)
            sleep(0.5)
        except Exception as e:
            LogUtil().warning(self.task_name, f'[BrowserRunner] 网页截图保存失败: {e}')
            return

        LogUtil().debug(self.task_name, f'[BrowserRunner] 网页截图保存成功: {screenshot_file_path}')


    def _stop_web_driver(self):
        """
        关闭浏览器实例
        """
        LogUtil().debug(self.task_name, "[BrowserRunner] 关闭浏览器")
        if self.web_driver:
            self.web_driver.quit()


    def get_request_thread_info(self):
        """
        返回request线程信息
        :return:
        """
        return {
            'request_type': RequestType.BROWSER_CHROME_SINGLE_TAB,
            'pid': self.network_service_pid
        }


    @staticmethod
    def create_request_thread_by_config(task_name: str, request_name: str, config: dict):
        return ChromeSingleTabRequest(
            task_name=task_name,
            request_name=request_name,
            url=config.get('url'),
            screenshot_dir=config.get('screenshot_dir'),
            screenshot_name=config.get('screenshot_name'),
            timeout=config.get('timeout'),
            wait_element_id=config.get('wait_element_id'),
            use_proxy=config.get('use_proxy'),
            proxy_port=config.get('proxy_port'),
        )
        pass
