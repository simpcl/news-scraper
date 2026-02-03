# News MCP Tools - Complete Documentation

A comprehensive Model Context Protocol (MCP) server that provides tools and resources for querying news from a PostgreSQL database through GraphQL API with Basic Authentication support.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Available Resources](#available-resources)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Overview

News MCP Tools provides a standardized interface for AI assistants to query news databases through GraphQL. It supports multiple query patterns including keyword search, source filtering, time range queries, and advanced multi-filter searches.

**Key Benefits:**
- No direct SQL queries - uses GraphQL API
- Server-side filtering and sorting for optimal performance
- Automatic time-based sorting (descending)
- Basic Authentication support
- 11 query tools + 3 data resources
- Easy integration with Claude Desktop and other MCP clients

## Features

- **11 Query Tools** for various news search scenarios
- **3 Resources** for quick data access
- **GraphQL API** based queries (no direct SQL)
- **Basic Authentication** support for secure API access
- **Server-side filtering** using GraphQL filter syntax
- **Server-side sorting** with `orderBy` parameter
- **Comprehensive error handling**

## Installation

### Prerequisites

1. **PostgreSQL with pg_graphql extension**
2. **Python 3.11+**
3. Required Python packages:

```bash
pip install fastmcp python-dotenv
```

### Files

| File | Description |
|------|-------------|
| `news_mcp.py` | MCP server with tools and resources |
| `pg_graphql.py` | GraphQL client with Basic Authentication |
| `example_usage.py` | Python usage examples |

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# GraphQL API endpoint (default: http://127.0.0.1:9782/rpc/graphql)
GRAPHQL_ENDPOINT=http://127.0.0.1:9782/rpc/graphql

# Basic Authentication (optional, required if API is protected)
BASIC_AUTH_USERNAME=your_username
BASIC_AUTH_PASSWORD=your_password

# PostgreSQL connection (optional, for direct database access)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=news_scraper
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
```

**Note:** The MCP server only requires `GRAPHQL_ENDPOINT`. The PostgreSQL connection variables are used by other tools in the pgrest module that need direct database access.

### Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

## Available Tools

### 1. get_latest_news

Get the most recent news items.

**Parameters:**
- `limit` (int, default: 10, max: 100) - Maximum number of news items

**Returns:**
```json
[
  {
    "id": 1,
    "title": "News Title",
    "url": "https://example.com/article",
    "source": "BBC",
    "time": "2025-01-15T10:30:00Z",
    "content": "Article content..."
  }
]
```

**Example:**
```python
# Get latest 10 news
news = get_latest_news(limit=10)
```

---

### 2. get_news_by_source

Filter news by source name (server-side filtering).

**Parameters:**
- `source` (str) - News source name (e.g., 'BBC', 'CNN', 'Reuters')
- `limit` (int, default: 10, max: 100) - Maximum number of items

**Example:**
```python
# Get news from BBC
bbc_news = get_news_by_source("BBC", limit=20)
```

---

### 3. search_news_by_keyword

Search for keyword in title (server-side filtering).

**Parameters:**
- `keyword` (str) - Keyword to search for in title
- `limit` (int, default: 10, max: 100) - Maximum number of items

**Example:**
```python
# Search for AI-related news
ai_news = search_news_by_keyword("AI", limit=15)
```

---

### 4. get_news_by_time_range

Get news within a specific time range (server-side filtering).

**Parameters:**
- `start_time` (str) - Start time in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
- `end_time` (str) - End time in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
- `limit` (int, default: 100, max: 500) - Maximum number of items

**Example:**
```python
# Get news from January 2025
jan_news = get_news_by_time_range(
    "2025-01-01",
    "2025-01-31",
    limit=100
)
```

---

### 5. get_news_today

Get all news from today.

**Parameters:**
- `limit` (int, default: 50, max: 200) - Maximum number of items

**Example:**
```python
# Get today's news
today_news = get_news_today(limit=50)
```

---

### 6. get_news_last_days

Get news from the last N days.

**Parameters:**
- `days` (int, default: 7) - Number of days to look back
- `limit` (int, default: 100, max: 500) - Maximum number of items

**Example:**
```python
# Get news from last 7 days
week_news = get_news_last_days(days=7, limit=100)
```

---

### 7. advanced_search

Advanced search with multiple filters (server-side filtering).

**Parameters:**
- `keyword` (str, optional) - Keyword to search for in title
- `source` (str, optional) - News source filter
- `start_time` (str, optional) - Start time
- `end_time` (str, optional) - End time
- `limit` (int, default: 50, max: 200) - Maximum number of items

**Example:**
```python
# Search AI news from BBC in last 3 days
results = advanced_search(
    keyword="AI",
    source="BBC",
    start_time="2025-01-12",
    end_time="2025-01-15",
    limit=50
)
```

---

### 8. get_news_statistics

Get statistics about the news database.

**Returns:**
```json
{
  "total_count": 1234,
  "sources": [
    {"source": "BBC", "count": 456},
    {"source": "CNN", "count": 234}
  ],
  "latest_news_time": "2025-01-15T10:30:00Z",
  "oldest_news_time": "2024-01-01T08:00:00Z"
}
```

**Example:**
```python
stats = get_news_statistics()
print(f"Total articles: {stats['total_count']}")
```

---

### 9. get_top_sources

Get top news sources by article count.

**Parameters:**
- `limit` (int, default: 10, max: 50) - Maximum number of sources

**Example:**
```python
# Get top 10 sources
top_sources = get_top_sources(limit=10)
```

---

### 10. get_news_by_id

Get a specific news item by its ID (server-side filtering).

**Parameters:**
- `news_id` (int) - The ID of the news item

**Returns:**
- News item dictionary or None if not found

**Example:**
```python
news_item = get_news_by_id(123)
```

---

### 11. get_news_titles_by_source

Lightweight query returning only titles by source (server-side filtering).

**Parameters:**
- `source` (str) - News source name
- `limit` (int, default: 20, max: 100) - Maximum number of items

**Returns:**
```json
[
  {"id": 1, "title": "News Title", "time": "2025-01-15T10:30:00Z"}
]
```

**Example:**
```python
titles = get_news_titles_by_source("BBC", limit=30)
```

## Available Resources

Resources provide read-only data access:

### news://sources
List all available news sources with article counts.

### news://statistics
Database statistics summary including totals and time ranges.

### news://latest
Latest news summary with formatted output.

## Usage Examples

### Example 1: Daily News Briefing

```python
from pgrest.news_mcp import get_news_today

# Get today's top news
today_news = get_news_today(limit=10)

print("Today's Top News:")
for i, news in enumerate(today_news, 1):
    print(f"{i}. {news['title']}")
    print(f"   Source: {news['source']}")
    print(f"   Time: {news['time']}")
    print()
```

### Example 2: Topic Research

```python
from pgrest.news_mcp import advanced_search
from datetime import datetime, timedelta

# Search AI news from last week
end_time = datetime.now()
start_time = end_time - timedelta(days=7)

results = advanced_search(
    keyword="AI",
    start_time=start_time.strftime("%Y-%m-%d"),
    end_time=end_time.strftime("%Y-%m-%d"),
    limit=50
)

print(f"Found {len(results)} AI-related articles from last week")
```

### Example 3: Source Analysis

```python
from pgrest.news_mcp import get_news_statistics, get_top_sources

# Get statistics
stats = get_news_statistics()
print(f"Total articles: {stats['total_count']}")
print(f"Latest: {stats['latest_news_time']}")
print(f"Oldest: {stats['oldest_news_time']}")

# Get top sources
top_sources = get_top_sources(limit=5)
print("\nTop 5 Sources:")
for source in top_sources:
    print(f"  {source['source']}: {source['count']} articles")
```

### Example 4: Time Range Query

```python
from pgrest.news_mcp import get_news_by_time_range

# Get news from specific date range
results = get_news_by_time_range(
    "2025-01-01 00:00:00",
    "2025-01-31 23:59:59",
    limit=100
)

print(f"Found {len(results)} articles in January 2025")
```

## Architecture

```
┌─────────────────────────────┐
│   MCP Client                │
│  (Claude Desktop / Other)   │
└──────────────┬──────────────┘
               │ MCP Protocol
               ▼
┌─────────────────────────────┐
│     news_mcp.py             │
│  - 11 Query Tools           │
│  - 3 Resources              │
│  - Server-side filtering    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   GraphQLClient             │
│  (pg_graphql.py)            │
│  - Basic Auth Support       │
│  - HTTP Request Handler     │
│  - execute_collection_query │
└──────────────┬──────────────┘
               │ HTTP POST + GraphQL
               ▼
┌─────────────────────────────┐
│  GraphQL API Endpoint       │
│  http://localhost:9782/... │
└──────────────┬──────────────┘
               │ pg_graphql
               ▼
┌─────────────────────────────┐
│  PostgreSQL Database        │
│  - news table               │
│  - pg_graphql extension     │
└─────────────────────────────┘
```

## API Reference

### GraphQL Query Structure

All tools use GraphQL queries with server-side filtering and sorting:

```graphql
query GetNews($first: Int, $filter: NewsFilter, $orderBy: NewsOrderBy) {
  newsCollection(first: $first, filter: $filter, orderBy: $orderBy) {
    edges {
      node {
        id
        title
        url
        source
        time
        content
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
      startCursor
    }
  }
}
```

### Filter Syntax

GraphQL filters use the following syntax:

```python
# Exact match
filter = {"source": {"eq": "BBC"}}

# Case-insensitive like search
filter = {"title": {"ilike": "%AI%"}}

# Greater than or equal
filter = {"time": {"gte": "2025-01-01"}}

# Less than or equal
filter = {"time": {"lte": "2025-01-31"}}

# Combined filters
filter = {
    "title": {"ilike": "%AI%"},
    "source": {"eq": "BBC"},
    "time": {"gte": "2025-01-01", "lte": "2025-01-31"}
}
```

### Order By Syntax

Server-side sorting using orderBy parameter:

```python
# Descending order with nulls last
order_by = {"time": "DescNullsLast"}

# Ascending order
order_by = {"title": "AscNullsFirst"}
```

### execute_collection_query Helper

All tools use the `execute_collection_query()` helper function from `pg_graphql.py`:

```python
def execute_collection_query(
    collection_name: str,
    first: int = 10,
    fields: Optional[List[str]] = None,
    after: Optional[str] = None,
    filter: Optional[Dict[str, Any]] = None,
    order_by: Optional[Dict[str, str]] = None,
) -> str:
```

This function:
- Builds GraphQL queries dynamically
- Handles filter and orderBy parameters
- Returns JSON formatted results
- Automatically adds the `id` field to all queries

### Response Format

All tools return data in this format:

```json
{
  "data": {
    "newsCollection": {
      "edges": [
        {
          "node": {
            "id": 1,
            "title": "...",
            "url": "...",
            "source": "...",
            "time": "...",
            "content": "..."
          },
          "cursor": "..."
        }
      ]
    }
  }
}
```

### Error Handling

All tools handle errors gracefully:

```python
try:
    result_json = execute_collection_query(
        collection_name="news",
        first=limit,
        fields=["title", "url", "source", "time", "content"],
        filter={"source": {"eq": source}},
        order_by={"time": "DescNullsLast"}
    )
    result = json.loads(result_json)
    return extract_nodes_from_result(result)
except Exception as e:
    return [{"error": f"Query failed: {str(e)}"}]
```

### Basic Authentication

When `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` are set, requests include:

```python
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Basic <base64(username:password)>"
}
```

## Troubleshooting

### Connection Issues

**Problem:** "Connection refused" error

**Solutions:**
1. Verify PostgreSQL is running
2. Check pg_graphql extension is installed
3. Test GraphQL endpoint:

```bash
curl -X POST http://127.0.0.1:9782/rpc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'
```

### Authentication Issues

**Problem:** 401 Unauthorized error

**Solutions:**
1. Verify BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD are set
2. Check credentials are correct
3. Test with curl:

```bash
curl -X POST http://127.0.0.1:9782/rpc/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <base64_credentials>" \
  -d '{"query": "{ __schema { queryType { name } } }"}'
```

### Module Import Error

**Problem:** "Module not found"

**Solutions:**
1. Install dependencies:
```bash
pip install fastmcp python-dotenv
```

2. Verify Python path includes project directory

### Testing

```bash
# Run example usage
python pgrest/example_usage.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python pgrest/news_mcp.py

# Test GraphQL endpoint directly
curl -X POST http://127.0.0.1:9782/rpc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __type(name: \"news\") { name fields { name } } }"}'
```

## Limitations

1. **Fetch limits** - Statistics are calculated from a limited fetch (500 records)
2. **GraphQL schema** - Limited to what pg_graphql provides
3. **Filter complexity** - Complex nested filters may not be supported

## Best Practices

1. **Use specific tools** - Use `get_news_today` instead of `get_news_by_time_range` for today's news
2. **Set reasonable limits** - Default limits are optimized for performance
3. **Use lightweight queries** - Use `get_news_titles_by_source` when you only need titles
4. **Cache results** - Consider caching frequently accessed data

## License

MIT
