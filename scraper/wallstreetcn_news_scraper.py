#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timedelta
import re
from .base_news_scraper import BaseNewsScraper, ListPageType


class WallStreetCNNewsScraper(BaseNewsScraper):
    def __init__(self, hours_ago=3):
        super().__init__(hours_ago)
        self.load_more_clicks = 5

    def clean_title(self, title_text):
        # 移除多余的换行符和空格
        title_text = " ".join(title_text.split())

        # 移除常见的无用字符
        title_text = title_text.replace("\n", "").replace("\r", "").replace("\t", "")

        return title_text.strip()

    def parse_time_string(self, time_text) -> datetime | None:
        try:
            # 移除可能的空白字符
            time_text = time_text.strip()

            dt = datetime.fromisoformat(time_text)
            # 如果有时区信息，转换为本地时间
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt

        except Exception as e:
            print(f"解析时间时发生错误: {e}, 时间字符串: {time_text}")
            return None

    def get_json_filename(self):
        return "wallstreetcn_news.json"

    def get_list_page_type(self):
        return ListPageType.LOAD_MORE

    def get_list_page_urls(self):
        return ["https://wallstreetcn.com/news/global"]

    def find_items_in_list_page(self):
        news_container = self.driver.find_element(By.CSS_SELECTOR, "div.article-list")
        print("成功找到指定的新闻列表容器")

        # 在容器内查找所有新闻项
        news_items = news_container.find_elements(
            By.CSS_SELECTOR, "div.article-entry.list-item"
        )

        return news_items

    def parse_list_page_item(self, item: WebElement):
        news_element = item
        title_text = None
        link_url = None
        source = "华尔街见闻"
        news_time = None

        try:
            # 查找标题链接 - 使用更灵活的方法
            a_element = news_element.find_element(By.TAG_NAME, "a")
            if a_element is None:
                raise Exception("a_element is None")
            span_element = a_element.find_element(By.TAG_NAME, "span")
            if span_element is None:
                raise Exception("span_element is None")
            title_text = span_element.text.strip()
            title_text = self.clean_title(title_text)
            link_url = a_element.get_attribute("href")
            if link_url is None or link_url == "":
                raise Exception("link_url is None or link_url == ''")

            time_element = news_element.find_element(By.CSS_SELECTOR, ".time")
            if time_element is None:
                raise Exception("time_element is None")
            time_element.get_attribute("datetime")
            time_text = time_element.get_attribute("datetime")
            news_time = self.parse_time_string(time_text)

            return title_text, link_url, source, news_time

        except Exception as e:
            print(f"解析新闻元素失败: {e}")
            return title_text, link_url, source, news_time

    def parse_content(self):
        content_body_element = self.driver.find_element(By.CSS_SELECTOR, ".article")
        if content_body_element is None:
            raise Exception("content_body_element is None")
        content = content_body_element.text.strip()
        return content


def main():
    scraper = None
    try:
        scraper = WallStreetCNNewsScraper()
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
