#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News Query MCP Server with PostgreSQL GraphQL Client
Provides various methods to query news through GraphQL API
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from fastmcp import FastMCP

from pg_graphql import GraphQLClient, execute_collection_query

# Create MCP server instance
mcp = FastMCP("News Query MCP Server")

# Initialize GraphQL client (lazy initialization)
_graphql_client = None

def get_client() -> GraphQLClient:
    """Get or initialize GraphQL client"""
    global _graphql_client
    if _graphql_client is None:
        _graphql_client = GraphQLClient()
    return _graphql_client


def extract_nodes_from_result(result: Dict) -> List[Dict]:
    """Extract nodes from GraphQL query result"""
    if "error" in result:
        return [{"error": result["error"]}]
    if "data" not in result:
        return []
    if "newsCollection" not in result["data"]:
        return []

    edges = result["data"]["newsCollection"]["edges"]
    return [edge["node"] for edge in edges]


@mcp.tool()
def get_latest_news(limit: int = 10) -> List[Dict]:
    """Get the latest news from the database

    Args:
        limit: Maximum number of news items to return (default: 10, max: 100)

    Returns:
        List of news items with fields: id, title, url, source, time, content
    """
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 10

    try:
        # Use server-side sorting by time descending
        result_json = execute_collection_query(
            collection_name="news",
            first=limit,
            fields=["title", "url", "source", "time", "content"],
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)
        return extract_nodes_from_result(result)
    except Exception as e:
        return [{"error": f"Query failed: {str(e)}"}]


@mcp.tool()
def get_news_by_source(source: str, limit: int = 10) -> List[Dict]:
    """Get news by source (client-side filtering)

    Args:
        source: News source name (e.g., 'BBC', 'CNN', 'Reuters')
        limit: Maximum number of news items to return (default: 10, max: 100)

    Returns:
        List of news items from the specified source
    """
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 10

    # Fetch more data for client-side filtering
    fetch_limit = min(limit * 5, 100)

    try:
        # Use server-side sorting by time descending
        result_json = execute_collection_query(
            collection_name="news",
            first=fetch_limit,
            fields=["title", "url", "source", "time", "content"],
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)
        nodes = extract_nodes_from_result(result)

        if nodes and "error" not in nodes[0]:
            # Client-side filtering by source
            filtered = [node for node in nodes if node.get('source') == source]
            return filtered[:limit]
        return nodes
    except Exception as e:
        return [{"error": f"Query failed: {str(e)}"}]


@mcp.tool()
def search_news_by_keyword(keyword: str, limit: int = 10) -> List[Dict]:
    """Search news by keyword in title and content (client-side filtering)

    Args:
        keyword: Keyword to search for
        limit: Maximum number of news items to return (default: 10, max: 100)

    Returns:
        List of news items containing the keyword
    """
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 10

    # Fetch more data for client-side filtering
    fetch_limit = min(limit * 5, 100)

    try:
        # Use server-side sorting by time descending
        result_json = execute_collection_query(
            collection_name="news",
            first=fetch_limit,
            fields=["title", "url", "source", "time", "content"],
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)
        nodes = extract_nodes_from_result(result)

        if nodes and "error" not in nodes[0]:
            # Client-side filtering
            keyword_lower = keyword.lower()
            filtered = [
                node for node in nodes
                if keyword_lower in node.get('title', '').lower() or keyword_lower in node.get('content', '').lower()
            ]
            return filtered[:limit]
        return nodes
    except Exception as e:
        return [{"error": f"Query failed: {str(e)}"}]


@mcp.tool()
def get_news_by_time_range(
    start_time: str,
    end_time: str,
    limit: int = 100
) -> List[Dict]:
    """Get news within a specific time range (client-side filtering)

    Args:
        start_time: Start time in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
        end_time: End time in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
        limit: Maximum number of news items to return (default: 100, max: 500)

    Returns:
        List of news items within the time range
    """
    if limit > 500:
        limit = 500
    if limit < 1:
        limit = 100

    # For time range filtering, we need to fetch more data
    fetch_limit = min(limit * 10, 500)

    try:
        # Use server-side sorting by time descending
        result_json = execute_collection_query(
            collection_name="news",
            first=fetch_limit,
            fields=["title", "url", "source", "time", "content"],
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)
        nodes = extract_nodes_from_result(result)

        if nodes and "error" not in nodes[0]:
            # Parse time range
            from datetime import datetime

            # Handle different time formats
            if len(start_time) == 10:
                start_dt = datetime.strptime(start_time, "%Y-%m-%d")
            elif len(start_time) == 19:
                start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            else:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

            if len(end_time) == 10:
                end_dt = datetime.strptime(end_time, "%Y-%m-%d")
            elif len(end_time) == 19:
                end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            else:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

            # Client-side filtering by time range
            filtered = []
            for node in nodes:
                node_time = node.get('time')
                if node_time:
                    try:
                        node_dt = datetime.fromisoformat(node_time.replace('Z', '+00:00'))
                        if start_dt <= node_dt <= end_dt:
                            filtered.append(node)
                    except:
                        continue

            return filtered[:limit]
        return nodes
    except Exception as e:
        return [{"error": f"Query failed: {str(e)}"}]


@mcp.tool()
def get_news_today(limit: int = 50) -> List[Dict]:
    """Get news from today

    Args:
        limit: Maximum number of news items to return (default: 50, max: 200)

    Returns:
        List of today's news items
    """
    if limit > 200:
        limit = 200
    if limit < 1:
        limit = 50

    today = datetime.now().strftime("%Y-%m-%d")
    return get_news_by_time_range(f"{today} 00:00:00", f"{today} 23:59:59", limit)


@mcp.tool()
def get_news_last_days(days: int = 7, limit: int = 100) -> List[Dict]:
    """Get news from the last N days

    Args:
        days: Number of days to look back (default: 7)
        limit: Maximum number of news items to return (default: 100, max: 500)

    Returns:
        List of news items from the last N days
    """
    if days < 1:
        days = 7
    if limit > 500:
        limit = 500
    if limit < 1:
        limit = 100

    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    return get_news_by_time_range(
        start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time.strftime("%Y-%m-%d %H:%M:%S"),
        limit
    )


@mcp.tool()
def advanced_search(
    keyword: Optional[str] = None,
    source: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """Advanced search with multiple filters (client-side filtering)

    Args:
        keyword: Optional keyword to search for in title and content
        source: Optional news source filter
        start_time: Optional start time in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
        end_time: Optional end time in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
        limit: Maximum number of news items to return (default: 50, max: 200)

    Returns:
        List of news items matching all specified filters
    """
    if limit > 200:
        limit = 200
    if limit < 1:
        limit = 50

    # Fetch more data for client-side filtering
    fetch_limit = min(limit * 20, 500)

    try:
        # Use server-side sorting by time descending
        result_json = execute_collection_query(
            collection_name="news",
            first=fetch_limit,
            fields=["title", "url", "source", "time", "content"],
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)
        nodes = extract_nodes_from_result(result)

        if nodes and "error" not in nodes[0]:
            filtered = nodes

            # Apply keyword filter
            if keyword:
                keyword_lower = keyword.lower()
                filtered = [
                    node for node in filtered
                    if keyword_lower in node.get('title', '').lower() or keyword_lower in node.get('content', '').lower()
                ]

            # Apply source filter
            if source:
                filtered = [node for node in filtered if node.get('source') == source]

            # Apply time range filter
            if start_time or end_time:
                from datetime import datetime

                if start_time:
                    if len(start_time) == 10:
                        start_dt = datetime.strptime(start_time, "%Y-%m-%d")
                    elif len(start_time) == 19:
                        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    else:
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                else:
                    start_dt = None

                if end_time:
                    if len(end_time) == 10:
                        end_dt = datetime.strptime(end_time, "%Y-%m-%d")
                    elif len(end_time) == 19:
                        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                    else:
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                else:
                    end_dt = None

                time_filtered = []
                for node in filtered:
                    node_time = node.get('time')
                    if node_time:
                        try:
                            node_dt = datetime.fromisoformat(node_time.replace('Z', '+00:00'))
                            if start_dt and node_dt < start_dt:
                                continue
                            if end_dt and node_dt > end_dt:
                                continue
                            time_filtered.append(node)
                        except:
                            continue
                filtered = time_filtered

            return filtered[:limit]
        return nodes
    except Exception as e:
        return [{"error": f"Query failed: {str(e)}"}]


@mcp.tool()
def get_news_statistics() -> Dict:
    """Get statistics about news in the database

    Returns:
        Dictionary containing:
        - total_count: Total number of news items
        - sources: List of sources with their counts
        - latest_news_time: Timestamp of the latest news
        - oldest_news_time: Timestamp of the oldest news
    """
    # Use a large fetch limit to get all data for statistics
    fetch_limit = 500

    try:
        # Use server-side sorting by time descending
        result_json = execute_collection_query(
            collection_name="news",
            first=fetch_limit,
            fields=["time", "source"],
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)

        if "error" in result:
            return {"error": result["error"]}
        if "data" not in result:
            return {"error": "No data returned"}

        edges = result["data"]["newsCollection"]["edges"]
        nodes = [edge["node"] for edge in edges]

        if not nodes:
            return {
                "total_count": 0,
                "sources": [],
                "latest_news_time": None,
                "oldest_news_time": None
            }

        # Calculate statistics
        total_count = len(nodes)
        times = [node["time"] for node in nodes if node.get("time")]
        sources = {}

        for node in nodes:
            source = node.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1

        # Sort sources by count
        sources_list = [
            {"source": k, "count": v}
            for k, v in sorted(sources.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "total_count": total_count,
            "sources": sources_list,
            "latest_news_time": max(times) if times else None,
            "oldest_news_time": min(times) if times else None
        }

    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool()
def get_top_sources(limit: int = 10) -> List[Dict]:
    """Get top news sources by article count

    Args:
        limit: Maximum number of sources to return (default: 10, max: 50)

    Returns:
        List of sources with their article counts
    """
    if limit > 50:
        limit = 50
    if limit < 1:
        limit = 10

    stats = get_news_statistics()

    if "error" in stats:
        return [{"error": stats["error"]}]

    return stats.get("sources", [])[:limit]


@mcp.tool()
def get_news_by_id(news_id: int) -> Optional[Dict]:
    """Get a specific news item by its ID (client-side filtering)

    Args:
        news_id: The ID of the news item

    Returns:
        News item details or None if not found
    """
    # Fetch a reasonable amount of data to find the ID
    fetch_limit = 100

    try:
        # Use server-side sorting by time descending
        result_json = execute_collection_query(
            collection_name="news",
            first=fetch_limit,
            fields=["title", "url", "source", "time", "content"],
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)
        nodes = extract_nodes_from_result(result)

        if nodes and "error" not in nodes[0]:
            # Client-side filtering by ID
            for node in nodes:
                if node.get('id') == news_id:
                    return node
            return None
        return None

    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool()
def get_news_titles_by_source(source: str, limit: int = 20) -> List[Dict]:
    """Get news titles only (lightweight query) by source (client-side filtering)

    Args:
        source: News source name
        limit: Maximum number of news items to return (default: 20, max: 100)

    Returns:
        List of news with id, title, time only
    """
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 20

    # Fetch more data for client-side filtering
    fetch_limit = min(limit * 5, 100)

    try:
        # Use server-side sorting by time descending
        result_json = execute_collection_query(
            collection_name="news",
            first=fetch_limit,
            fields=["title", "time", "source"],
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)
        nodes = extract_nodes_from_result(result)

        if nodes and "error" not in nodes[0]:
            # Client-side filtering by source
            filtered = [node for node in nodes if node.get('source') == source]
            # Return only id, title, time
            result = [
                {"id": n["id"], "title": n["title"], "time": n["time"]}
                for n in filtered[:limit]
            ]
            return result
        return nodes
    except Exception as e:
        return [{"error": f"Query failed: {str(e)}"}]


@mcp.resource("news://sources")
def get_sources_resource() -> str:
    """Get all available news sources as a resource"""
    sources = get_top_sources(50)

    if sources and "error" in sources[0]:
        return f"Error fetching sources: {sources[0]['error']}"

    output = "Available news sources:\n"
    output += "=" * 40 + "\n"
    for source in sources:
        output += f"- {source['source']}: {source['count']} articles\n"

    return output


@mcp.resource("news://statistics")
def get_statistics_resource() -> str:
    """Get news statistics as a resource"""
    stats = get_news_statistics()

    if "error" in stats:
        return f"Error fetching statistics: {stats['error']}"

    output = "News Database Statistics\n"
    output += "=" * 40 + "\n"
    output += f"Total articles: {stats['total_count']}\n"
    output += f"Latest news: {stats['latest_news_time']}\n"
    output += f"Oldest news: {stats['oldest_news_time']}\n\n"

    output += "Articles by source:\n"
    for source in stats['sources'][:10]:
        output += f"  - {source['source']}: {source['count']}\n"

    return output


@mcp.resource("news://latest")
def get_latest_news_resource() -> str:
    """Get latest news as a readable resource"""
    news_list = get_latest_news(5)

    if news_list and "error" in news_list[0]:
        return f"Error fetching news: {news_list[0]['error']}"

    output = "Latest News\n"
    output += "=" * 40 + "\n"

    for i, news in enumerate(news_list, 1):
        output += f"\n{i}. {news['title']}\n"
        output += f"   Source: {news['source']}\n"
        output += f"   Time: {news['time']}\n"
        output += f"   URL: {news['url']}\n"

    return output


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
