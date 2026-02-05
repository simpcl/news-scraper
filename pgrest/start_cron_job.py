import schedule
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

import news_mcp_example
def job(time_range):
    print("starting the cron job...")

    output_filepath = "../data/news_merged.json"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=time_range)
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    limit = 90

    news_mcp_example.download_jsonfile_by_time_range(output_filepath, start_time_str, end_time_str, limit)


if __name__ == '__main__':
    load_dotenv()

    job(12)

    # schedule.every(10).seconds.do(job)
    schedule.every().day.at("07:30").do(job, 12)
    schedule.every().day.at("19:30").do(job, 5)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

