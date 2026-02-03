#!/usr/bin/env python3

import json

from pg_graphql import execute_collection_query

def interactive_query_news():
    print("\n\n=== Interactive News Query From PostgreSQL GraphQL ===")
    print("Type 'quit' to exit")

    while True:
        try:
            print("\nPlease select an operation:")
            print("1. Get news by count")
            print("2. Search news")
            print("3. Exit")

            choice = input("\nPlease enter choice (1-3): ").strip()

            if choice == "1":
                count = input("Please enter number of news items to get: ").strip()
                if count.isdigit():
                    count = int(count)
                    result_json = execute_collection_query(
                        collection_name="news",
                        fields=["id", "title", "url", "source", "time"],
                        first=count,
                        order_by={"time": "DescNullsLast"}
                    )
                    result = json.loads(result_json)
                    edges = result["data"]["newsCollection"]["edges"]

                    print(f"\nRetrieved {len(edges)} news items:")
                    for i, edge in enumerate(edges, 1):
                        node = edge["node"]
                        print(f"{i}. {node['title']}")
                        print(f"   Source: {node['source']} | Time: {node['time']}")
                        print()
                else:
                    print("Please enter a valid number")

            elif choice == "2":
                keyword = input("Please enter search keyword: ").strip()
                if keyword:
                    print(f"\nSearching for news containing '{keyword}'...")
                    result_json = execute_collection_query(
                        collection_name="news",
                        fields=["id", "title", "url", "source", "time"],
                        first=100,
                        order_by={"time": "DescNullsLast"}
                    )
                    result = json.loads(result_json)
                    edges = result["data"]["newsCollection"]["edges"]

                    # Client-side filtering
                    filtered_news = []
                    for edge in edges:
                        node = edge["node"]
                        if keyword.lower() in node["title"].lower():
                            filtered_news.append(node)

                    if filtered_news:
                        print(f"\nFound {len(filtered_news)} related news:")
                        for i, news in enumerate(
                            filtered_news[:10], 1
                        ):  # Show first 10
                            print(f"{i}. {news['title']}")
                            print(f"   Source: {news['source']} | Time: {news['time']}")
                            print()
                    else:
                        print(f"No news found containing '{keyword}'")

            elif choice == "3":
                print("Exit")
                break

            else:
                print("Invalid choice, please try again")

        except KeyboardInterrupt:
            print("\n\nExit")
            break
        except Exception as e:
            print(f"\nOperation failed: {str(e)}")


if __name__ == "__main__":
    try:
        interactive_query_news()
    except (KeyboardInterrupt, EOFError):
        print("\n === Program ended ===")
