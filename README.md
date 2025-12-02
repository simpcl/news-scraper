# News Scraper (新闻爬虫)

一个多线程的新闻内容抓取工具，支持从多个中文财经新闻网站抓取最新的新闻内容。

## 支持的新闻网站

- 东方财富网
- 财联社
- 财联社头条
- 同花顺
- 华尔街见闻

## 功能特性

- 🚀 **多线程并发抓取**：支持同时抓取多个网站的新闻
- 📅 **时间范围过滤**：可设置抓取指定时间范围内的新闻
- 🔄 **自动合并**：将多个网站的新闻自动合并为一个文件
- 🌐 **动态内容支持**：支持抓取JavaScript动态加载的内容
- 📱 **无头模式**：支持在服务器环境下运行，无需图形界面
- 💾 **JSON格式输出**：所有抓取结果以JSON格式保存

## 环境要求

- Python 3.11+
- Chrome 浏览器
- Linux/Windows/macOS

## 安装步骤

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd news-scraper
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

复制并编辑环境变量配置文件：

```bash
cp config.env.example .env
```

编辑 `.env` 文件：

```env
# 数据保存目录
DATA_DIR=./data

# 抓取时间范围（小时）
TIME_RANGE=3

# 最大并发线程数
MAX_WORKERS=5
```

### 配置说明

- **DATA_DIR**: 新闻数据保存目录，默认为 `./data`
- **TIME_RANGE**: 抓取多少小时内的新闻，范围1-24小时，默认3小时
- **MAX_WORKERS**: 最大并发线程数，范围1-10，默认5

## 使用方法

### 1. 命令行使用

直接运行主程序：

```bash
python cli.py
```

程序将使用默认配置抓取所有支持网站的新闻。

### 2. 自定义参数使用

可以通过修改 `cli.py` 中的参数来自定义抓取行为：

```python
params = {
    "websites": ["东方财富网", "财联社"],  # 指定要抓取的网站
    "time_range": 6,                      # 抓取6小时内的新闻
    "max_workers": 3                      # 使用3个并发线程
}
```

### 3. 单独使用各个抓取器

```python
from eastmoney_news_scraper import EastMoneyNewsScraper

# 创建抓取器实例，抓取6小时内的新闻
scraper = EastMoneyNewsScraper(hours_ago=6)

# 开始抓取
filename = scraper.scrape_news()

# 关闭浏览器
scraper.close()
```

## 输出格式

每个网站的新闻将保存为独立的JSON文件：

- `eastmoney_news.json` - 东方财富网新闻
- `cls_news.json` - 财联社新闻
- `cls_headline_news.json` - 财联社头条新闻
- `jqka_news.json` - 同花顺新闻
- `wallstreetcn_news.json` - 华尔街见闻新闻

所有新闻将自动合并为：

- `news_merged.json` - 合并后的所有新闻

### JSON格式示例

```json
{
    "scrape_time": "2025-01-02 14:30:00",
    "total_count": 50,
    "news_list": [
        {
            "title": "新闻标题",
            "url": "https://example.com/news/123",
            "source": "新闻来源",
            "time": "2025-01-02 14:00:00",
            "content": "新闻正文内容..."
        }
    ]
}
```

## 许可证

本项目采用 [BSD 3-Clause License](LICENSE) 开源协议。
