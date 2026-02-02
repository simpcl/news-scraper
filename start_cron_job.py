import schedule
import os
import time
from dotenv import load_dotenv
from scraper.cli import Cli
from merger.news_merger import NewsMerger

def job(time_range):
    print("starting the cron job...")
    
    params = { 
        "websites": ["东方财富网", "财联社", "财联社头条", "同花顺", "华尔街见闻"],
        "time_range": time_range,  # hours
        "max_workers": int(os.environ.get("MAX_WORKERS", "5")),
        "max_retry": int(os.environ.get("MAX_RETRY", "3"))
    }   

    cli = Cli()
    cli.run(params)

    data_dir = os.environ.get("DATA_DIR", ".")
    news_merger = NewsMerger()
    news_merger.run(data_dir)


if __name__ == '__main__':
    load_dotenv()

    #schedule.every(10).seconds.do(job)
    schedule.every().day.at("07:30").do(job, 12)
    schedule.every().day.at("19:30").do(job, 5)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
