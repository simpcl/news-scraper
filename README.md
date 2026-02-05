# News Scraper (新闻爬虫)

一个多线程的新闻内容抓取、存储和查询系统，支持从多个中文财经新闻网站抓取最新的新闻内容，并提供PostgreSQL数据库存储、GraphQL查询接口和MCP服务器。

## 支持的新闻网站

- 东方财富网
- 财联社
- 财联社头条
- 同花顺
- 华尔街见闻

## 功能特性

### 核心功能
- 🚀 **多线程并发抓取**：支持同时抓取多个网站的新闻
- 📅 **时间范围过滤**：可设置抓取指定时间范围内的新闻
- 🔄 **自动重试机制**：支持失败任务自动重试，提高成功率
- 🔄 **自动合并**：将多个网站的新闻自动合并为一个文件
- 🌐 **动态内容支持**：支持抓取JavaScript动态加载的内容
- 📱 **无头模式**：支持在服务器环境下运行，无需图形界面
- 💾 **JSON格式输出**：所有抓取结果以JSON格式保存

### 数据管理
- 🗄️ **PostgreSQL存储**：自动将新闻数据存入PostgreSQL数据库
- 🔍 **GraphQL查询**：提供GraphQL API接口查询新闻数据
- 🤖 **MCP服务器**：支持通过Model Context Protocol访问新闻数据
- ⏰ **定时任务**：支持定时抓取和自动更新
- 📊 **统计分析**：提供新闻数量、来源分布等统计功能

## 项目结构

```
news-scraper/
├── scraper/              # 新闻抓取器模块
│   ├── base_news_scraper.py         # 基础抓取器类
│   ├── cli.py                       # 命令行接口
│   ├── eastmoney_news_scraper.py    # 东方财富网抓取器
│   ├── cls_news_scraper.py          # 财联社抓取器
│   ├── cls_headline_news_scraper.py # 财联社头条抓取器
│   ├── jqka_news_scraper.py         # 同花顺抓取器
│   └── wallstreetcn_news_scraper.py # 华尔街见闻抓取器
├── dao/                  # 数据访问层
│   ├── db_config.py      # 数据库配置
│   ├── db_init.py        # 数据库初始化
│   └── news_dao.py       # 新闻数据访问对象
├── merger/               # 新闻合并模块
│   └── news_merger.py    # 新闻文件合并器
├── pgrest/               # PostgreSQL REST和GraphQL模块
│   ├── pg_graphql.py     # GraphQL客户端
│   ├── news_mcp.py       # MCP服务器
│   ├── news_mcp_example.py   # MCP使用示例
│   └── README_NEWS_MCP.md    # MCP功能文档
├── utils/                # 工具模块
│   └── utils.py          # 工具函数
├── start_cron_job.py     # 定时任务主程序
├── requirements.txt      # Python依赖
└── config.env.example    # 环境变量配置示例
```

## 环境要求

- Python 3.11+
- Chrome 浏览器
- PostgreSQL 13+ (含 pg_graphql 扩展)
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

### 4. 配置PostgreSQL数据库

确保已安装PostgreSQL并启用pg_graphql扩展：

```sql
-- 创建数据库
CREATE DATABASE news_scraper;

-- 连接到数据库
\c news_scraper

-- 启用pg_graphql扩展
CREATE EXTENSION pg_graphql;
```

或者运行项目自带的初始化脚本（首次运行时自动创建）。

## 配置

复制并编辑环境变量配置文件：

```bash
cp config.env.example .env
```

编辑 `.env` 文件：

```env
# 数据保存目录
DATA_DIR=./data

# Selenium页面加载超时时间（秒）
SELENIUM_PAGE_LOAD_TIMEOUT=30

# 抓取时间范围（小时）
TIME_RANGE=3

# 最大并发线程数
MAX_WORKERS=5

# 抓取失败时的最大重试次数
MAX_RETRY=1

# PostgreSQL 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=news_scraper
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# GraphQL API 配置
GRAPHQL_ENDPOINT=http://127.0.0.1:9782/rpc/graphql
BASIC_AUTH_USERNAME=
BASIC_AUTH_PASSWORD=
```

### 配置说明

#### 基础配置
- **DATA_DIR**: 新闻数据保存目录，默认为 `./data`
- **SELENIUM_PAGE_LOAD_TIMEOUT**: Selenium页面加载超时时间（秒），默认30秒
- **TIME_RANGE**: 抓取多少小时内的新闻，范围1-24小时，默认3小时
- **MAX_WORKERS**: 最大并发线程数，范围1-10，默认5
- **MAX_RETRY**: 抓取失败时的最大重试次数，范围0-10，默认1次

#### 数据库配置
- **POSTGRES_HOST**: PostgreSQL服务器地址，默认localhost
- **POSTGRES_PORT**: PostgreSQL端口，默认5432
- **POSTGRES_DB**: 数据库名称，默认news_scraper
- **POSTGRES_USER**: 数据库用户名
- **POSTGRES_PASSWORD**: 数据库密码

#### GraphQL配置
- **GRAPHQL_ENDPOINT**: GraphQL API端点地址
- **BASIC_AUTH_USERNAME**: Basic认证用户名（可选）
- **BASIC_AUTH_PASSWORD**: Basic认证密码（可选）

## 使用方法

### 1. 基础抓取

直接运行抓取器：

```bash
cd scraper
python cli.py
```

程序将使用默认配置抓取所有支持网站的新闻。

### 2. 自定义参数抓取

可以通过修改 `cli.py` 中的参数来自定义抓取行为：

```python
from scraper.cli import Cli

params = {
    "websites": ["东方财富网", "财联社"],  # 指定要抓取的网站
    "time_range": 6,                      # 抓取6小时内的新闻
    "max_workers": 3,                     # 使用3个并发线程
    "max_retry": 5                        # 失败时最多重试5次
}

cli = Cli()
cli.run(params)
```

### 3. 单独使用各个抓取器

```python
from scraper.eastmoney_news_scraper import EastMoneyNewsScraper

# 创建抓取器实例，抓取6小时内的新闻
scraper = EastMoneyNewsScraper(hours_ago=6)

# 开始抓取
filename = scraper.scrape_news()

# 关闭浏览器
scraper.close()
```

### 4. 定时任务抓取

运行定时任务，自动定时抓取新闻并保存到数据库：

```bash
python start_cron_job.py
```

定时任务会：
1. 按配置的时间范围抓取所有网站新闻
2. 合并所有新闻到一个JSON文件
3. 自动将新闻数据导入PostgreSQL数据库
4. 按设定间隔重复执行（默认为 TIME_RANGE - 1 小时）

可以在 `start_cron_job.py` 中自定义定时规则：

```python
# 每天07:30和19:30执行
schedule.every().day.at("07:30").do(job, 12)
schedule.every().day.at("19:30").do(job, 5)

# 每10秒执行一次（测试用）
schedule.every(10).seconds.do(job)

# 每N小时执行一次
schedule.every(time_range - 1).hours.do(job, time_range)
```

### 5. 数据库操作

使用DAO (Data Access Object) 操作数据库：

```python
from dao.news_dao import NewsDAO

# 初始化DAO（自动创建数据库和表）
dao = NewsDAO()

# 从JSON文件导入数据
dao.load_from_json_file("data/news_merged.json")

# 按来源查询新闻
news_list = dao.get_news_by_source("东方财富网", limit=10)

# 按时间范围查询
news_list = dao.get_news_by_time_range("2025-01-01", "2025-01-31")

# 关键词搜索
news_list = dao.search_news_by_keyword("人工智能", limit=20)

# 获取最新新闻
latest_news = dao.get_latest_news(limit=10)

# 获取统计数据
stats = dao.get_news_count_by_source()
total = dao.get_total_count()

# 清理旧数据
dao.delete_old_news(days=30)
```

命令行方式使用DAO：

```bash
# 显示数据库统计信息
python -m dao.news_dao show

# 导入JSON数据
python -m dao.news_dao import --json data/news_merged.json
```

### 6. GraphQL查询

使用GraphQL API查询数据：

```python
from pgrest.pg_graphql import GraphQLClient

# 创建客户端
client = GraphQLClient()

# 执行查询
query = """
query {
    newsCollection(first: 10, orderBy: {time: DescNullsLast}) {
        edges {
            node {
                id
                title
                url
                source
                time
            }
        }
    }
}
"""

result = client.execute_query(query)
print(result)
```

### 7. 使用MCP服务器

MCP服务器提供了丰富的查询工具，可与Claude Desktop等MCP客户端集成。

详细文档请参考：[pgrest/README_NEWS_MCP.md](pgrest/README_NEWS_MCP.md)

主要功能：

#### 10个查询工具
1. `get_latest_news` - 获取最新新闻
2. `get_news_by_source` - 按来源查询
3. `get_news_by_time_range` - 按时间范围查询
4. `get_news_today` - 获取今日新闻
5. `get_news_last_days` - 获取最近N天的新闻
6. `advanced_search_news` - 高级搜索（支持多条件过滤）
7. `get_news_statistics` - 获取数据库统计
8. `get_top_sources` - 获取主要新闻来源
9. `get_news_by_id` - 根据ID查询新闻
10. `get_news_titles_by_source` - 获取来源新闻标题（轻量查询）

#### 3个数据资源
- `news://sources` - 所有新闻来源
- `news://statistics` - 数据库统计
- `news://latest` - 最新新闻摘要

#### Claude Desktop配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "news-query": {
      "command": "python",
      "args": ["/path/to/news-scraper/pgrest/news_mcp.py"],
      "env": {
        "GRAPHQL_ENDPOINT": "http://127.0.0.1:9782/rpc/graphql",
        "BASIC_AUTH_USERNAME": "your_username",
        "BASIC_AUTH_PASSWORD": "your_password"
      }
    }
  }
}
```

### 8. 新闻合并

手动合并多个新闻JSON文件：

```python
from merger.news_merger import NewsMerger
import os

merger = NewsMerger()
data_dir = os.environ.get("DATA_DIR", "./data")
output_file = os.path.join(data_dir, "news_merged.json")

merger.run(data_dir, output_file)
```

## 输出格式

### 文件输出

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

### 数据库表结构

PostgreSQL数据库包含以下表：

#### news表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键，自增 |
| title | VARCHAR(500) | 新闻标题 |
| url | VARCHAR(1000) | 新闻链接（唯一索引） |
| source | VARCHAR(100) | 新闻来源 |
| time | TIMESTAMP | 发布时间 |
| content | TEXT | 新闻内容 |
| created_at | TIMESTAMP | 记录创建时间 |

索引：
- `idx_news_url` - URL唯一索引
- `idx_news_source` - 来源索引
- `idx_news_time` - 时间索引
- `idx_news_title` - 标题索引（用于全文搜索）

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户接口层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ CLI工具  │  │定时任务  │  │ MCP服务  │  │GraphQL   │   │
│  │          │  │          │  │          │  │  API     │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
┌───────┼─────────────┼─────────────┼─────────────┼──────────┐
│       ▼             ▼             ▼             ▼          │
│                     业务逻辑层                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  抓取器 (Scrapers)                                    │  │
│  │  - BaseNewsScraper (基类)                            │  │
│  │  - EastMoney, CLS, JQKA, WallStreetCN (实现类)     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ 合并器   │  │  DAO     │  │ MCP工具  │               │
│  │Merger    │  │          │  │          │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└────────────────────────────────────────────────────────────┘
        │             │             │
┌───────┼─────────────┼─────────────┼──────────────────────┐
│       ▼             ▼             ▼                      │
│                     数据层                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │           PostgreSQL 数据库                       │    │
│  │  - news表                                        │    │
│  │  - pg_graphql扩展                                │    │
│  └──────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────┐    │
│  │           JSON文件存储                            │    │
│  │  - data/*.json                                   │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

## 开发指南

### 添加新的新闻网站抓取器

1. 在 `scraper/` 目录创建新的抓取器类
2. 继承 `BaseNewsScraper`
3. 实现所有抽象方法
4. 在 `cli.py` 中注册新的网站

详细开发指南请参考：[scraper/README.md](scraper/README.md)

### 扩展MCP工具

在 `pgrest/news_mcp.py` 中添加新的工具函数：

```python
@mcp.tool()
def your_new_tool(param: str) -> str:
    """Tool description"""
    # 实现逻辑
    return result
```

## 最佳实践

### 1. 抓取性能优化

- **合理设置并发数**：`MAX_WORKERS` 建议设置为3-5
- **适当的时间范围**：`TIME_RANGE` 不宜过长，建议3-6小时
- **使用定时任务**：避免手动频繁执行
- **服务器环境**：使用无头模式提高性能

### 2. 数据库维护

- **定期清理**：使用 `delete_old_news()` 清理过期数据
- **索引优化**：定期执行 `VACUUM ANALYZE`
- **备份策略**：定期备份新闻数据库

### 3. 错误处理

- **重试机制**：设置合理的 `MAX_RETRY` 值
- **超时设置**：根据网络情况调整 `SELENIUM_PAGE_LOAD_TIMEOUT`
- **日志监控**：关注抓取日志，及时发现问题

### 4. 安全建议

- **密码管理**：不要将 `.env` 文件提交到版本控制
- **认证保护**：生产环境建议启用GraphQL Basic认证
- **访问控制**：限制数据库访问权限

## 故障排除

### 问题1: Chrome驱动失败

**错误信息**: `SessionNotCreatedException: Message: Unable to find a matching set of chrome driver`

**解决方案**:
- 确保已安装Chrome浏览器
- `webdriver-manager` 会自动下载匹配的驱动
- 检查网络连接

### 问题2: 数据库连接失败

**错误信息**: `could not connect to server: Connection refused`

**解决方案**:
- 确认PostgreSQL服务正在运行
- 检查 `.env` 中的数据库配置
- 验证数据库用户权限

### 问题3: 页面加载超时

**错误信息**: `TimeoutException: Message: Timeout loading page`

**解决方案**:
- 增加 `SELENIUM_PAGE_LOAD_TIMEOUT` 值
- 检查网络连接
- 验证目标网站是否可访问

### 问题4: GraphQL查询失败

**错误信息**: `401 Unauthorized` 或查询返回空

**解决方案**:
- 确认pg_graphql扩展已安装
- 检查GraphQL端点配置
- 验证Basic认证凭据（如果启用）

## 相关文档

- [抓取器详细文档](scraper/README.md) - 抓取器开发和使用指南
- [MCP服务器文档](pgrest/README_NEWS_MCP.md) - MCP工具和API参考

## 许可证

本项目采用 [BSD 3-Clause License](LICENSE) 开源协议。
