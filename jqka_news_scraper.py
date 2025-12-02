from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from abc import abstractmethod
from base_news_scraper import BaseNewsScraper, ListPageType
import re
from datetime import datetime


class JQKANewsScraper(BaseNewsScraper):
    def __init__(self, hours_ago=3):
        super().__init__(hours_ago)

    def clean_title(self, title_text):
        """
        清理标题文本
        :param title_text: 原始标题文本
        :return: 清理后的标题文本
        """
        # 移除多余的换行符和空格
        title_text = " ".join(title_text.split())

        # 移除常见的无用字符
        title_text = title_text.replace("\n", "").replace("\r", "").replace("\t", "")

        return title_text.strip()

    def parse_time_string(self, time_text):
        """
        解析时间字符串，转换为datetime对象
        :param time_text: 时间字符串，如 "09月21日 11:27"
        :return: datetime对象，解析失败返回None
        """
        try:
            # 移除可能的空白字符
            time_text = time_text.strip()

            # 匹配格式：09月21日 11:27
            pattern = r"(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):(\d{2})"
            match = re.match(pattern, time_text)

            if match:
                month, day, hour, minute = match.groups()
                # 假设是当前年份
                current_year = datetime.now().year
                return datetime(
                    current_year, int(month), int(day), int(hour), int(minute)
                )
            else:
                print(f"无法解析时间格式: {time_text}")
                return None

        except Exception as e:
            print(f"解析时间时发生错误: {e}, 时间字符串: {time_text}")
            return None

    def get_json_filename(self):
        return "jqka_news.json"

    def get_list_page_type(self):
        return ListPageType.PAGINATION

    def get_list_page_urls(self):
        url_tmpl = "https://news.10jqka.com.cn/today_list/index_{}.shtml"
        urls = []
        for i in range(1, 6):
            urls.append(url_tmpl.format(i))
        return urls

    def find_items_in_list_page(self):
        news_container = self.driver.find_element(By.CSS_SELECTOR, "div.list-con")

        print("成功找到指定的新闻列表容器标签")
        news_items = news_container.find_elements(By.TAG_NAME, "li")

        return news_items

    def parse_list_page_item(self, item: WebElement):
        li_element = item
        title_text = None
        link_url = None
        news_time = None
        source = "同花顺"

        try:
            # 查找包含标题和时间的span元素
            arc_title_element = li_element.find_element(
                By.CSS_SELECTOR, "span.arc-title"
            )
            if arc_title_element is None:
                raise Exception("arc_title_element is None")

            # 查找标题链接
            title_link = arc_title_element.find_element(By.TAG_NAME, "a")
            if title_link is None:
                raise Exception("title_link is None")

            title_text = title_link.text.strip()
            title_text = self.clean_title(title_text)
            link_url = title_link.get_attribute("href")

            if link_url is None or link_url == "":
                raise Exception("link_url is None or link_url == ''")

            # 查找时间元素 - 在arc-title内的span元素中
            time_spans = arc_title_element.find_elements(By.TAG_NAME, "span")
            for span in time_spans:
                span_text = span.text.strip()
                # 检查是否包含时间格式（月日 时:分）
                if re.search(r"\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{2}", span_text):
                    news_time = self.parse_time_string(span_text)
                    break

            if news_time is None:
                raise Exception("news_time is None")

            return title_text, link_url, source, news_time

        except Exception as e:
            print(f"解析li元素中的新闻标题链接时间失败: {e}")
            return title_text, link_url, source, news_time

    def parse_content(self):
        content_body_element = self.driver.find_element(By.ID, "contentApp")
        if content_body_element is None:
            raise Exception("content_body_element is None")
        content = content_body_element.text.strip()
        return content


def main():
    scraper = None
    try:
        # 创建爬虫实例
        scraper = JQKANewsScraper()
        print("开始抓取新闻...")
        scraper.scrape_news()
        print("抓取新闻完成")

    except Exception as e:
        print(f"程序执行失败: {e}")

    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
