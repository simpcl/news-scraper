#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财联社新闻抓取器 - 无头模式优化版
"""

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
import json
import os
from datetime import datetime, timedelta
import re
from .base_news_scraper import BaseNewsScraper, ListPageType


class CLSNewsScraper(BaseNewsScraper):
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

            if "小时前" in time_text:
                # 提取小时数
                hour_match = re.search(r"(\d+)小时前", time_text)
                if hour_match:
                    hours_ago = int(hour_match.group(1))
                    return datetime.now() - timedelta(hours=hours_ago)
            elif "分钟前" in time_text:
                # 提取分钟数
                minute_match = re.search(r"(\d+)分钟前", time_text)
                if minute_match:
                    minutes_ago = int(minute_match.group(1))
                    return datetime.now() - timedelta(minutes=minutes_ago)
            elif "天前" in time_text:
                # 提取天数
                day_match = re.search(r"(\d+)天前", time_text)
                if day_match:
                    days_ago = int(day_match.group(1))
                    return datetime.now() - timedelta(days=days_ago)
            else:
                raise Exception("time_text is not a relative time")

        except Exception as e:
            print(f"解析时间时发生错误: {e}, 时间字符串: {time_text}")
            return None

    def click_load_more_button(self):
        for i in range(self.load_more_clicks):
            try:
                print(f"第 {i+1} 次尝试点击'加载更多'按钮...")

                # 滚动到页面底部，确保按钮可见
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(2)

                # 记录点击前的新闻数量
                news_count_before = len(
                    self.driver.find_elements(
                        By.CSS_SELECTOR, "div.subject-interest-image-content-box.p-r"
                    )
                )

                # 通过文本内容查找按钮
                load_more_button = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'more-button') and contains(text(), '加载更多')]",
                )

                # 确保按钮可见
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", load_more_button
                )
                time.sleep(1)

                # 尝试点击按钮
                try:
                    load_more_button.click()
                    print(f"成功点击'加载更多'按钮 (第 {i+1} 次)")
                except Exception as click_error:
                    print(f"点击按钮失败: {click_error}，尝试使用JavaScript点击")
                    try:
                        self.driver.execute_script(
                            "arguments[0].click();", load_more_button
                        )
                        print(f"通过JavaScript成功点击'加载更多'按钮 (第 {i+1} 次)")
                    except Exception as js_click_error:
                        print(f"JavaScript点击也失败: {js_click_error}")
                        break

                # 等待新内容加载
                time.sleep(3)

                # 等待JavaScript执行完成
                self.wait_for_javascript_completion()

                # 检查是否有新内容加载
                news_count_after = len(
                    self.driver.find_elements(
                        By.CSS_SELECTOR,
                        "div.subject-interest-image-content-box.p-r",
                    )
                )

                if news_count_after > news_count_before:
                    print(
                        f"成功加载新内容，新闻数量从 {news_count_before} 增加到 {news_count_after}"
                    )
                else:
                    print("未检测到新内容加载，可能已到达页面底部")
                    break

            except NoSuchElementException:
                print(f"未找到'加载更多'按钮 (第 {i+1} 次尝试)")

            except Exception as e:
                print(f"点击'加载更多'按钮时发生错误 (第 {i+1} 次): {e}")
                break

        print(f"完成点击'加载更多'按钮，共尝试了 {i+1} 次")

    def get_json_filename(self):
        return "cls_news.json"

    def get_list_page_type(self):
        return ListPageType.LOAD_MORE

    def get_list_page_urls(self):
        return ["https://www.cls.cn/depth?id=1000"]

    def find_items_in_list_page(self):
        news_container = self.driver.find_element(By.CSS_SELECTOR, "div.depth-list-box")
        print("成功找到指定的新闻列表容器")

        # 在容器内查找所有新闻项
        news_items = news_container.find_elements(
            By.CSS_SELECTOR, "div.subject-interest-image-content-box.p-r"
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
            div_element = news_element.find_element(
                By.CSS_SELECTOR, "div.subject-interest-title"
            )
            if div_element is None:
                raise Exception("div_element is None")
            a_element = div_element.find_element(By.TAG_NAME, "a")
            if a_element is None:
                raise Exception("a_element is None")
            title_text = a_element.text.strip()
            title_text = self.clean_title(title_text)
            link_url = a_element.get_attribute("href")
            if link_url is None or link_url == "":
                raise Exception("link_url is None or link_url == ''")

            span_time_element = news_element.find_element(By.CSS_SELECTOR, "span.m-r-5")
            if span_time_element is None:
                raise Exception("span_time_element is None")
            time_text = span_time_element.text.strip()
            news_time = self.parse_time_string(time_text)

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
        scraper = CLSNewsScraper()
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
