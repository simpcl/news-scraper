from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys
from abc import abstractmethod
from datetime import datetime, timedelta
from enum import Enum
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import utils


class ListPageType(Enum):
    PAGINATION = 1
    LOAD_MORE = 2


class BaseNewsScraper:
    def __init__(self, hours_ago=3):
        self.news_after_time = datetime.now() - timedelta(hours=hours_ago)
        self.data_dir = os.environ.get("DATA_DIR", ".")
        self.page_load_timeout = int(os.environ.get("SELENIUM_PAGE_LOAD_TIMEOUT", "30"))
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """设置Chrome浏览器驱动 - Linux无头模式优化"""
        chrome_options = Options()

        # 强制无头模式
        chrome_options.add_argument("--headless")

        # Linux服务器环境优化参数
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")

        # 内存和性能优化
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        chrome_options.add_argument("--window-size=1920,1080")

        # 网络优化
        chrome_options.add_argument("--aggressive-cache-discard")
        chrome_options.add_argument("--disable-background-networking")

        # 用户代理
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # 禁用图片加载以提高速度（可选）
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # 禁用扩展和插件
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")

        try:
            # 使用webdriver-manager自动管理ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            # Set page load timeout from environment variable
            self.driver.set_page_load_timeout(self.page_load_timeout)
            print(f"Chrome浏览器驱动初始化成功 (无头模式, 页面加载超时: {self.page_load_timeout}秒)")
        except Exception as e:
            print(f"初始化Chrome驱动失败: {e}")
            print("请确保已安装Chrome浏览器")
            raise

    def wait_for_javascript_completion(self):
        """等待JavaScript执行完成"""
        print("等待JavaScript执行完成...")
        try:
            # 等待jQuery加载完成（如果页面使用jQuery）
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script(
                    "return typeof jQuery !== 'undefined' ? jQuery.active == 0 : true"
                )
            )
        except TimeoutException:
            print("jQuery检查超时，继续执行...")

        # 等待页面状态稳定
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )
        except TimeoutException:
            print("页面状态检查超时，继续执行...")

        # 额外等待时间确保动态内容加载
        time.sleep(2)
        print("JavaScript执行完成")

    def scroll_to_load_content(self):
        """滚动页面以触发懒加载内容"""
        print("滚动页面以触发懒加载...")
        try:
            # 多次滚动以触发所有可能的懒加载
            for i in range(3):
                print(f"滚动尝试 {i+1}/3")

                # 获取页面高度
                last_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )

                # 滚动到页面底部
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(1)  # 增加等待时间

                # 检查是否有新内容加载
                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_height > last_height:
                    print(
                        f"检测到新内容加载，页面高度从 {last_height} 增加到 {new_height}"
                    )
                    time.sleep(2)
                else:
                    print("未检测到新内容加载")

                # 尝试滚动到中间位置
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight/2);"
                )
                time.sleep(1)

            # 滚动回顶部
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

        except Exception as e:
            print(f"滚动操作失败: {e}")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

    def save_to_json_file(self, news_list, filename=None):
        """
        保存结果到JSON文件
        :param news_list: 新闻列表
        :param filename: 保存文件名
        """
        try:
            if news_list is None:
                raise Exception("news_list is None")
            if filename is None or filename == "":
                raise Exception("filename is None or filename == ''")
            # 添加抓取时间戳
            result_data = {
                "scrape_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": len(news_list),
                "news_list": news_list,
            }
            output_filepath = os.path.join(self.data_dir, filename)
            return utils.save_to_json_file(result_data, output_filepath)
        except Exception as e:
            print(f"保存抓取文件失败: {e}")
            return None

    def click_load_more_button(self):
        pass

    def scrape_news_list(self, url=None, news_after_time=None):
        """
        抓取指定页面的新闻标题和链接
        :param url: 目标页面URL
        :param news_after_time: 新闻时间过滤条件
        :param load_more_clicks: 点击"加载更多"按钮的次数，默认为3次
        :return: 包含新闻标题和链接的列表
        """
        if url is None:
            url = self.scrape_url
        if news_after_time is None:
            news_after_time = self.news_after_time

        try:
            print(f"正在访问页面: {url}")
            self.driver.get(url)

            # 等待页面完全加载，包括JavaScript执行
            print("等待页面完全加载...")
            time.sleep(3)  # 初始等待时间

            # 等待JavaScript执行完成
            self.wait_for_javascript_completion()

            # 尝试滚动页面以触发懒加载
            self.scroll_to_load_content()

            # # 额外等待，尝试让更多内容加载
            # print("额外等待以加载更多内容...")
            # time.sleep(3)

            # 循环点击"加载更多"按钮
            if self.get_list_page_type() == ListPageType.LOAD_MORE:
                self.click_load_more_button()
            elif self.get_list_page_type() == ListPageType.PAGINATION:
                pass
            else:
                raise Exception("Invalid list page type")

            news_list = []
            try:
                print("查找列表页面中的新闻项...")
                news_items = self.find_items_in_list_page()
                print(f"在列表页面中找到 {len(news_items)} 个新闻项")

                for item in news_items:
                    title, url, source, news_time = self.parse_list_page_item(item)
                    if title is None or url is None or source is None:
                        continue
                    if news_after_time and news_time:
                        if news_time <= news_after_time:
                            continue

                    news_item = {
                        "title": title,
                        "url": url,
                        "source": source,
                    }
                    if news_time:
                        news_item["time"] = news_time.strftime("%Y-%m-%d %H:%M:%S")
                    news_list.append(news_item)
                    print(f"找到新闻: {title} (时间: {news_time})")

            except NoSuchElementException as e:
                print(f"未找到HTML标签或类名, {e}")
                print(f"完整栈信息:\n{traceback.format_exc()}")
                return []

            except Exception as e:
                print(f"查找HTML标签或类名失败: {e}")
                print(f"完整栈信息:\n{traceback.format_exc()}")
                return []

            # 去重和排序
            unique_news = []
            seen_titles = set()

            for news in news_list:
                if news["title"] not in seen_titles:
                    unique_news.append(news)
                    seen_titles.add(news["title"])

            print(f"去重后共找到 {len(unique_news)} 条新闻")
            return unique_news

        except Exception as e:
            print(f"抓取过程中发生错误: {e}")
            return []

    def scrape_news_content(self, url):
        try:
            print(f"正在访问页面: {url}")
            self.driver.get(url)
            time.sleep(3)
            self.wait_for_javascript_completion()
            # self.scroll_to_load_content()
            # time.sleep(1)
            content = self.parse_content()
            if content is None:
                raise Exception("Content is None")
            return content
        except NoSuchElementException:
            print("未找到指定的HTML标签或类名")
            return None
        except Exception as e:
            print(f"抓取新闻内容失败: {e}")
            return None

    def scrape_news(self):
        merged_news_list = []

        list_page_urls = self.get_list_page_urls()
        for list_page_url in list_page_urls:
            news_list = self.scrape_news_list(list_page_url)
            if news_list:
                print(f"\n成功抓取到 {len(news_list)} 条新闻:")
                for i, news in enumerate(news_list, 1):
                    print(f"{i}. {news['title']}")
                    print(f"   链接: {news['url']}")
                    if "time" in news:
                        print(f"   时间: {news['time']}")
                    else:
                        print("   时间: 未知")
                    print(f"   来源: {news['source']}")
                    print()
                merged_news_list.extend(news_list)
            else:
                print("未找到任何新闻")
                break

        for news_item in merged_news_list:
            print(f"抓取新闻内容: {news_item['title']}")
            content = self.scrape_news_content(news_item["url"])
            if content is not None:
                news_item["content"] = content

        return self.save_to_json_file(merged_news_list, self.get_json_filename())

    @abstractmethod
    def get_json_filename(self):
        return ""

    @abstractmethod
    def get_list_page_type(self):
        return ListPageType.PAGINATION

    @abstractmethod
    def get_list_page_urls(self):
        """
        获取列表页面的URL
        """
        return []

    @abstractmethod
    def find_items_in_list_page(self):
        """
        查找列表页面中的新闻项
        """
        return []

    @abstractmethod
    def parse_list_page_item(self, item: WebElement):
        """
        解析列表页面
        """
        title = None
        url = None
        source = None
        time = None
        return title, url, source, time

    @abstractmethod
    def parse_content(self):
        """
        解析内容
        """
        content = None
        return content
