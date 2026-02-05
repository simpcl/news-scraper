#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: How to use the News Query Functions

This example demonstrates how to use the GraphQL client to query news.
This is the underlying implementation used by the News MCP Server.
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
from typing import List, Dict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pg_graphql import GraphQLClient, execute_collection_query
import news_mcp


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

def download_jsonfile_by_time_range(output_filepath, start_time_str, end_time_str, limit=10):
    try:
        print(f"Fetching news from {start_time_str} to {end_time_str}...\n")
        news_list = news_mcp.get_news_by_time_range.fn(start_time_str, end_time_str, limit)

        # datadir, filename = os.path.split(output_filepath)
        # os.makedirs(datadir, exist_ok=True)
        result = {}
        result["total_count"] = len(news_list)
        result["news_list"] = news_list

        with open(output_filepath, "w", encoding="utf-8") as f:
            result_json = json.dumps(result, ensure_ascii=False, indent=4)
            f.write(result_json)
        print(f"download_jsonfile_by_time_range successfully: {output_filepath}")
    except Exception as e:
        print(f"download_jsonfile_by_time_range failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="News MCP Wrapper")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    download_parser = subparsers.add_parser("download", help="Download json file")
    download_parser.add_argument(
        "--json", nargs="?", default="", help="Download JSON File Path (e.g.: news.json)"
    )
    download_parser.add_argument(
        "--last_hours", nargs="?", default="3", help="Last X hours (e.g.: 3)"
    )
    download_parser.add_argument(
        "--limit", nargs="?", default="10", help="News items limit (e.g.: 10)"
    )

    args = parser.parse_args()

    if args.command and args.command == "download":
        if not args.json:
            print("请指定JSON文件路径")
            exit(-1)

        hours = int(args.last_hours)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        if not args.limit:
            limit = int(args.limit)
            download_jsonfile_by_time_range(args.json, start_time_str, end_time_str, limit)
        else:
            download_jsonfile_by_time_range(args.json, start_time_str, end_time_str)
    else:
        print("请选择要执行的命令")