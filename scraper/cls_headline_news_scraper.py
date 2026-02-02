from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import re

from base_news_scraper import BaseNewsScraper, ListPageType

class CLSHeadlineNewsScraper(BaseNewsScraper):
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

    def get_json_filename(self):
        return "cls_headline_news.json"

    def get_list_page_type(self):
        return ListPageType.PAGINATION

    def get_list_page_urls(self):
        return ["https://www.cls.cn/depth?id=1000"]

    def find_items_in_list_page(self):
        news_items = self.driver.find_elements(
            By.CSS_SELECTOR, "div.depth-top-article-list"
        )

        return news_items

    def parse_list_page_item(self, item: WebElement):
        news_element = item
        title_text = None
        link_url = None
        source = "财联社"
        news_time = None

        try:
            # 查找标题链接 - 使用更灵活的方法
            title_links = news_element.find_elements(By.TAG_NAME, "a")
            if title_links:
                # 选择第一个有文本内容的链接
                for link in title_links:
                    link_text = link.text.strip()
                    if link_text and len(link_text) > 5:  # 确保是有效的标题
                        title_text = self.clean_title(link_text)
                        link_url = link.get_attribute("href")
                        break

            # 如果没有找到链接，尝试从元素文本中提取标题
            if not title_text:
                element_text = news_element.text.strip()
                if element_text and len(element_text) > 5:
                    # 清理文本，移除时间信息
                    lines = element_text.split("\n")
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 5 and not re.match(r".*小时前.*", line):
                            title_text = self.clean_title(line)
                            break

            return title_text, link_url, source, news_time

        except Exception as e:
            print(f"解析新闻元素失败: {e}")
            return title_text, link_url, source, news_time

    def parse_content(self):
        content_body_element = self.driver.find_element(
            By.CSS_SELECTOR, "div.f-l.w-894"
        )
        if content_body_element is None:
            raise Exception("content_body_element is None")
        content = content_body_element.text.strip()
        return content


def main():
    scraper = None
    try:
        # 创建爬虫实例
        scraper = CLSHeadlineNewsScraper()
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
