from typing import List, Union
import os
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper.eastmoney_news_scraper import EastMoneyNewsScraper
from scraper.cls_news_scraper import CLSNewsScraper
from scraper.cls_headline_news_scraper import CLSHeadlineNewsScraper
from scraper.jqka_news_scraper import JQKANewsScraper
from scraper.wallstreetcn_news_scraper import WallStreetCNNewsScraper
from news_merger import NewsMerger
import utils


class Cli:
    def __init__(self):
        pass
    def run(self, params: Union[str, dict]) -> bool:
        if not "websites" in params:
            print("无效的新闻网站列表")
            return False

        if not "time_range" in params:
            params["time_range"] = 6
        if params["time_range"] < 1 or params["time_range"] > 24:
            print("无效的时间范围")
            return False

        if not "max_workers" in params:
            params["max_workers"] = 3
        if params["max_workers"] < 1 or params["max_workers"] > 10:
            print("不支持的最大并发工作线程数")
            return False

        if not "max_retry" in params:
            params["max_retry"] = 3
        if params["max_retry"] < 0 or params["max_retry"] > 10:
            print("不支持的最大重试次数")
            return False

        # 创建抓取任务列表
        scrape_tasks = []
        for website in params["websites"]:
            if website == "东方财富网":
                scraper_class = EastMoneyNewsScraper
            elif website == "财联社":
                scraper_class = CLSNewsScraper
            elif website == "财联社头条":
                scraper_class = CLSHeadlineNewsScraper
            elif website == "同花顺":
                scraper_class = JQKANewsScraper
            elif website == "华尔街见闻":
                scraper_class = WallStreetCNNewsScraper
            else:
                print(f"不支持的新闻网站: {website}")
                continue
            scrape_tasks.append((website, scraper_class, params["time_range"], params["max_retry"]))

        if len(scrape_tasks) == 0:
            return False

        self._run_scrape_tasks(scrape_tasks, params["max_workers"])

        self._merge_news_files()
    def _run_scrape_tasks(self, scrape_tasks, max_workers=3):
        print(f"开始并发抓取 {len(scrape_tasks)} 个网站的新闻...")
        successful_scrapes = []
        failed_scrapes = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有抓取任务
            future_to_website = {
                executor.submit(
                    self._scrape_single_website, website, scraper_class, time_range, max_retry
                ): website
                for website, scraper_class, time_range, max_retry in scrape_tasks
            }

            # 收集结果
            for future in as_completed(future_to_website):
                website = future_to_website[future]
                try:
                    result = future.result()
                    if result:
                        successful_scrapes.append((website, result))
                    else:
                        failed_scrapes.append(website)
                except Exception as e:
                    failed_scrapes.append(website)
                    print(f"✗ {website} 抓取时发生严重异常: {e}")

        # 汇总结果
        print(
            f"\n抓取完成！成功: {len(successful_scrapes)}, 失败: {len(failed_scrapes)}"
        )
        if failed_scrapes:
            print(f"失败的网站: {', '.join(failed_scrapes)}")
        if not successful_scrapes:
            print("所有网站抓取都失败了")

    def _merge_news_files(self) -> str:
        print("开始合并 *_news.json 文件...")
        try:
            news_merger = NewsMerger()
            merged_data = news_merger.merge_news_files()
            if merged_data is None or "news_list" not in merged_data:
                print("合并的数据为空")
                return False
            if len(merged_data["news_list"]) == 0:
                print("没有找到可合并的数据")
                return False

            data_dir = os.environ.get("DATA_DIR", ".")
            file_path = utils.save_to_json_file(merged_data, data_dir, "news_merged.json")
            print(f"合并结果已保存到: {file_path}")
        except Exception as e:
            print(f"合并文件时发生错误: {e}")
            return False
        return True

    def _scrape_single_website(
        self, website: str, scraper_class, time_range: int, max_retry: int = 3
    ) -> str:
        """
        抓取单个网站的新闻，支持重试机制
        :param website: 网站名称
        :param scraper_class: 抓取器类
        :param time_range: 时间范围
        :param max_retry: 最大重试次数
        :return: 文件名，失败返回None
        """
        for retry_count in range(max_retry + 1):  # +1 because we include the first attempt
            scraper = None
            try:
                if retry_count > 0:
                    print(f"开始第 {retry_count} 次重试 {website}...")
                    # 重试前等待一段时间
                    time.sleep(5 * retry_count)  # 递增等待时间：5秒, 10秒, 15秒...
                else:
                    print(f"开始抓取 {website} 新闻...")

                scraper = scraper_class(time_range)
                filename = scraper.scrape_news()
                if filename:
                    return filename
            except Exception as e:
                print(f"✗ {website} 抓取异常: {e}")
            finally:
                if scraper:
                    try:
                        scraper.close()
                    except Exception as e:
                        print(f"关闭 {website} 抓取器时发生异常: {e}")

        return None

if __name__ == "__main__":
    load_dotenv()
    
    params = {
        "websites": ["东方财富网", "财联社", "财联社头条", "同花顺", "华尔街见闻"],
        "time_range": int(os.environ.get("TIME_RANGE", "1")),  # hours
        "max_workers": int(os.environ.get("MAX_WORKERS", "5")),
        "max_retry": int(os.environ.get("MAX_RETRY", "3"))
    }

    cli = Cli()
    cli.run(params)
