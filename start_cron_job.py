import schedule
import os
import time
from dotenv import load_dotenv
from cli import Cli

def job(time_range):
    print("starting the morning job...")

    load_dotenv()
    
    params = { 
        "websites": ["东方财富网", "财联社", "财联社头条", "同花顺", "华尔街见闻"],
        "time_range": time_range,  # hours
        "max_workers": int(os.environ.get("MAX_WORKERS", "5")),
        "max_retry": int(os.environ.get("MAX_RETRY", "3"))
    }   

    cli = Cli()
    cli.run(params)


if __name__ == '__main__':
    #schedule.every(10).seconds.do(job)
    schedule.every().day.at("07:30").do(job, 12)
    schedule.every().day.at("19:30").do(job, 5)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
