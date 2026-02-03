import schedule
import os, sys
import time
from dotenv import load_dotenv

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_dir, "scraper"))
sys.path.append(os.path.join(project_dir, "dao"))

from scraper.cli import Cli
from merger.news_merger import NewsMerger
from dao.news_dao import NewsDAO

def job(time_range):
    print("starting the cron job...")
    
    params = { 
        "websites": ["东方财富网", "财联社", "财联社头条", "同花顺", "华尔街见闻"],
        "time_range": time_range,  # hours
        "max_workers": int(os.environ.get("MAX_WORKERS", "5")),
        "max_retry": int(os.environ.get("MAX_RETRY", "1"))
    }

    cli = Cli()
    cli.run(params)

    data_dir = os.environ.get("DATA_DIR", ".")
    output_json_filepath = os.path.join(data_dir, "news_merged.json")
    news_merger = NewsMerger()
    news_merger.run(data_dir, output_json_filepath)

    newsDao = NewsDAO()
    newsDao.load_from_json_file(output_json_filepath)


if __name__ == '__main__':
    load_dotenv()

    time_range = int(os.environ.get("TIME_RANGE", "3"))
    if time_range < 2:
        time_range = 2

    job(time_range)

    # schedule.every(10).seconds.do(job)
    # schedule.every().day.at("07:30").do(job, 12)
    # schedule.every().day.at("19:30").do(job, 5)
    schedule.every(time_range - 1).hours.do(job, time_range)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
