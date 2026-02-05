# News Scraper Modules

This directory contains the core scraper modules for the news scraping system.

## Architecture Overview

The scraper system follows an object-oriented design pattern with a base class providing common functionality and individual scraper implementations for each news website.

```
scraper/
├── base_news_scraper.py          # Base scraper class with common functionality
├── cli.py                        # Command-line interface for running scrapers
├── eastmoney_news_scraper.py     # East Money (东方财富网) scraper
├── cls_news_scraper.py           # CLS (财联社) scraper
├── cls_headline_news_scraper.py  # CLS Headline (财联社头条) scraper
├── jqka_news_scraper.py          # Tonghuashun (同花顺) scraper
└── wallstreetcn_news_scraper.py  # Wall Street CN (华尔街见闻) scraper
```

## Base News Scraper (`base_news_scraper.py`)

The `BaseNewsScraper` is an abstract base class that provides common functionality for all scrapers.

### Key Features

- **Headless Chrome Driver**: Automatically manages ChromeDriver using webdriver-manager
- **JavaScript Handling**: Waits for JavaScript execution and lazy-loaded content
- **Time Filtering**: Filters news by publication time
- **Content Extraction**: Scrapes both news list pages and individual article content
- **Data Persistence**: Saves results to JSON files

### List Page Types

The base class supports two types of news list pages:

```python
class ListPageType(Enum):
    PAGINATION = 1    # Traditional pagination (page 1, 2, 3, ...)
    LOAD_MORE = 2     # "Load More" button style infinite scroll
```

### Abstract Methods

Each scraper must implement the following methods:

| Method | Return Type | Description |
|--------|-------------|-------------|
| `get_json_filename()` | `str` | Returns the output JSON filename |
| `get_list_page_type()` | `ListPageType` | Returns the type of list page |
| `get_list_page_urls()` | `List[str]` | Returns list of list page URLs to scrape |
| `find_items_in_list_page()` | `List[WebElement]` | Finds news items in the list page |
| `parse_list_page_item(item)` | `Tuple[str, str, str, datetime]` | Parses a single list item (title, url, source, time) |
| `parse_content()` | `str` | Parses the article content page |

### Common Methods

| Method | Description |
|--------|-------------|
| `setup_driver()` | Initializes Chrome driver with headless mode and Linux optimizations |
| `wait_for_javascript_completion()` | Waits for jQuery and page state to complete |
| `scroll_to_load_content()` | Scrolls page to trigger lazy-loaded content |
| `click_load_more_button()` | Clicks "Load More" button (override in subclasses) |
| `scrape_news_list(url, news_after_time)` | Scrapes news list from a URL |
| `scrape_news_content(url)` | Scrapes content from a news article URL |
| `scrape_news()` | Main method: scrapes all news and saves to JSON |
| `save_to_json_file(news_list, filename)` | Saves news list to JSON file |
| `close()` | Closes the browser driver |

### Initialization Parameters

```python
scraper = ExampleScraper(hours_ago=3)
```

- `hours_ago`: Only scrape news published within this many hours (default: 3)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `.` | Directory for output JSON files |
| `SELENIUM_PAGE_LOAD_TIMEOUT` | `30` | Page load timeout in seconds |

## Individual Scrapers

### East Money Scraper (`eastmoney_news_scraper.py`)

**Source**: East Money (东方财富网)
**Output File**: `eastmoney_news.json`
**List Page Type**: `PAGINATION`
**URL Pattern**: `https://finance.eastmoney.com/a/cywjh_{page}.html` (pages 1-5)

**Time Format**: `YYYY年MM月DD日 HH:MM`

**Key Methods**:
- `clean_title(title_text)`: Removes extra whitespace and special characters
- `parse_time_string(time_text)`: Parses Chinese date format

### CLS Scraper (`cls_news_scraper.py`)

**Source**: CLS (财联社)
**Output File**: `cls_news.json`
**List Page Type**: `LOAD_MORE`
**URL**: `https://www.cls.cn/depth?id=1000`

**Time Format**: Relative time (`X小时前`, `X分钟前`, `X天前`)

**Features**:
- Automatically clicks "Load More" button up to 5 times
- Converts relative time to absolute datetime

### CLS Headline Scraper (`cls_headline_news_scraper.py`)

**Source**: CLS Headline (财联社头条)
**Output File**: `cls_headline_news.json`
**List Page Type**: `PAGINATION`
**URL**: `https://www.cls.cn/depth?id=1000`

**Features**:
- Scrapes headline articles from depth page
- Does not filter by time

### Tonghuashun Scraper (`jqka_news_scraper.py`)

**Source**: Tonghuashun (同花顺)
**Output File**: `jqka_news.json`
**List Page Type**: `PAGINATION`
**URL Pattern**: `https://news.10jqka.com.cn/today_list/index_{page}.shtml` (pages 1-5)

**Time Format**: `MM月DD日 HH:MM`

**Features**:
- Assumes current year for dates
- Parses time from nested span elements

### Wall Street CN Scraper (`wallstreetcn_news_scraper.py`)

**Source**: Wall Street CN (华尔街见闻)
**Output File**: `wallstreetcn_news.json`
**List Page Type**: `LOAD_MORE`
**URL**: `https://wallstreetcn.com/news/global`

**Time Format**: ISO 8601 format

**Features**:
- Parses ISO format datetime with timezone support
- Converts to local timezone

## Command Line Interface (`cli.py`)

The `Cli` class provides a concurrent scraping interface for multiple websites.

### Usage

```python
from cli import Cli

params = {
    "websites": ["东方财富网", "财联社", "财联社头条", "同花顺", "华尔街见闻"],
    "time_range": 6,        # Scrape news from last 6 hours
    "max_workers": 3,       # Use 3 concurrent threads
    "max_retry": 5          # Retry failed attempts up to 5 times
}

cli = Cli()
cli.run(params)
```

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `websites` | `List[str]` | - | - | List of website names to scrape |
| `time_range` | `int` | 1-24 | 6 | Hours of news to scrape |
| `max_workers` | `int` | 1-10 | 3 | Maximum concurrent threads |
| `max_retry` | `int` | 0-10 | 3 | Maximum retry attempts |

### Supported Website Names

- `"东方财富网"` - East Money
- `"财联社"` - CLS
- `"财联社头条"` - CLS Headline
- `"同花顺"` - Tonghuashun
- `"华尔街见闻"` - Wall Street CN

### Features

- **Concurrent Execution**: Uses `ThreadPoolExecutor` for parallel scraping
- **Retry Mechanism**: Automatically retries failed scrapers with exponential backoff
- **Progress Tracking**: Reports success/failure for each website

## Creating a New Scraper

To add support for a new news website, create a new class inheriting from `BaseNewsScraper`:

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from base_news_scraper import BaseNewsScraper, ListPageType

class NewWebsiteScraper(BaseNewsScraper):
    def __init__(self, hours_ago=3):
        super().__init__(hours_ago)

    def get_json_filename(self):
        return "newwebsite_news.json"

    def get_list_page_type(self):
        return ListPageType.PAGINATION  # or ListPageType.LOAD_MORE

    def get_list_page_urls(self):
        # Return list of URLs to scrape
        return ["https://example.com/news/page1"]

    def find_items_in_list_page(self):
        # Find and return news item elements
        container = self.driver.find_element(By.CSS_SELECTOR, "div.news-list")
        return container.find_elements(By.TAG_NAME, "article")

    def parse_list_page_item(self, item: WebElement):
        # Extract title, URL, source, and time from item
        title = item.find_element(By.TAG_NAME, "h2").text
        url = item.find_element(By.TAG_NAME, "a").get_attribute("href")
        source = "Example Website"
        time = self.parse_time(item.find_element(By.CLASS_NAME, "time").text)
        return title, url, source, time

    def parse_content(self):
        # Extract article content
        content = self.driver.find_element(By.CLASS_NAME, "article-content").text
        return content

    def parse_time(self, time_text):
        # Parse time string to datetime object
        # Implement your time parsing logic here
        pass
```

### Tips for New Scrapers

1. **Inspect the Website**: Use browser developer tools to find CSS selectors
2. **Handle Dynamic Content**: Use `wait_for_javascript_completion()` and `scroll_to_load_content()`
3. **Parse Time Correctly**: Implement `parse_time_string()` to handle the website's time format
4. **Clean Titles**: Use `clean_title()` to remove extra whitespace
5. **Handle Errors**: Always wrap Selenium operations in try-except blocks
6. **Test Headless Mode**: Ensure the scraper works without a display

## Common Issues and Solutions

### Issue: NoSuchElementException

**Solution**: Add explicit waits using `WebDriverWait`:

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(self.driver, 10)
element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "selector")))
```

### Issue: Timeout on Page Load

**Solution**: Increase `SELENIUM_PAGE_LOAD_TIMEOUT` environment variable:

```bash
export SELENIUM_PAGE_LOAD_TIMEOUT=60
```

### Issue: Content Not Loading

**Solution**: Extend wait times in `wait_for_javascript_completion()` or add custom waits:

```python
time.sleep(5)  # Wait for dynamic content
```

### Issue: Chrome Driver Not Found

**Solution**: The base class uses `webdriver-manager` to automatically download the correct ChromeDriver version. Ensure Chrome browser is installed:

```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser

# macOS
brew install --cask google-chrome
```

## Dependencies

- `selenium` - Web browser automation
- `webdriver-manager` - Automatic ChromeDriver management
- `python-dotenv` - Environment variable management

## Example Usage

### Single Scraper

```python
from eastmoney_news_scraper import EastMoneyNewsScraper

scraper = EastMoneyNewsScraper(hours_ago=6)
filename = scraper.scrape_news()
print(f"News saved to: {filename}")
scraper.close()
```

### Multiple Scrapers with CLI

```python
from cli import Cli

params = {
    "websites": ["东方财富网", "财联社"],
    "time_range": 3,
    "max_workers": 2,
    "max_retry": 3
}

cli = Cli()
cli.run(params)
```

### Custom List Page URL Scraping

```python
from cls_news_scraper import CLSNewsScraper

scraper = CLSNewsScraper(hours_ago=6)
news_list = scraper.scrape_news_list(url="https://www.cls.cn/depth?id=1000")
for news in news_list:
    print(f"{news['title']} - {news['time']}")
scraper.close()
```

## Output Format

All scrapers output JSON files with the following structure:

```json
{
    "scrape_time": "2025-01-02 14:30:00",
    "total_count": 50,
    "news_list": [
        {
            "title": "News Title",
            "url": "https://example.com/news/123",
            "source": "News Source",
            "time": "2025-01-02 14:00:00",
            "content": "Full article content..."
        }
    ]
}
```

## License

This project is licensed under the BSD 3-Clause License. See the main LICENSE file for details.
