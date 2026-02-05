#!/usr/bin/env python3

import json

from pg_graphql import GraphQLClient

def query_news():
    print("\n=== News Query From PostgreSQL GraphQL ===")

    try:
        print("\nGetting latest 3 news items...")
        query = """
        query {
            newsCollection(first: 3) {
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
        client = GraphQLClient()
        result = client.execute_query(query=query)
        edges = result["data"]["newsCollection"]["edges"]

        print(f"\n✓ Successfully retrieved {len(edges)} news items:")
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
