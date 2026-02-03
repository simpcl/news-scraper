#!/usr/bin/env python3

import json

from pg_graphql import execute_collection_query

def query_news():
    print("\n=== News Query From PostgreSQL GraphQL ===")
    print("\nGet latest 3 news items:\n")

    try:
        result_json = execute_collection_query(
            collection_name="news",
            fields=["id", "title", "url", "source", "time"],
            first=3,
            order_by={"time": "DescNullsLast"}
        )
        result = json.loads(result_json)
        if "error" in result:
            print(f"✗ graphql_query tool failed: {result['error']}")
        else:
            print("✓ graphql_query tool executed successfully")

            edges = result["data"]["newsCollection"]["edges"]

            print(f"✓ Successfully retrieved {len(edges)} news items:\n")

            for i, edge in enumerate(edges, 1):
                node = edge["node"]
                print(f"{i}. 📰 {node['title']}")
                print(f"   🔗 Link: {node['url']}")
                print(f"   📰 Source: {node['source']}")
                print(f"   ⏰ Time: {node['time']}")
                print()
    except Exception as e:
        print(f"✗ Query failed: {str(e)}")

if __name__ == "__main__":
    query_news()
