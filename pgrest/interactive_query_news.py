#!/usr/bin/env python3

from pg_graphql import GraphQLClient

def interactive_query_news():
    print("\n\n=== Interactive News Query From PostgreSQL GraphQL ===")
    print("Type 'quit' to exit")

    client = GraphQLClient()

    while True:
        try:
            print("\nPlease select an operation:")
            print("1. Get latest news")
            print("2. Get news by count")
            print("3. Search news")
            print("4. Exit")

            choice = input("\nPlease enter choice (1-4): ").strip()

            if choice == "1":
                print("\nGetting latest 5 news items...")
                query = """
                query {
                  newsCollection(first: 5) {
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

                result = client.execute_query(query=query)
                edges = result["data"]["newsCollection"]["edges"]

                print(f"\nRetrieved {len(edges)} news items:")
                for i, edge in enumerate(edges, 1):
                    node = edge["node"]
                    print(f"{i}. {node['title']}")
                    print(f"   Source: {node['source']} | Time: {node['time']}")
                    print()

            elif choice == "2":
                count = input("Please enter number of news items to get: ").strip()
                if count.isdigit():
                    count = int(count)
                    query = f"""
                    query {{
                      newsCollection(first: {count}) {{
                        edges {{
                          node {{
                            id
                            title
                            url
                            source
                            time
                          }}
                        }}
                      }}
                    }}
                    """

                    result = client.execute_query(query=query)
                    edges = result["data"]["newsCollection"]["edges"]

                    print(f"\nRetrieved {len(edges)} news items:")
                    for i, edge in enumerate(edges, 1):
                        node = edge["node"]
                        print(f"{i}. {node['title']}")
                        print(f"   Source: {node['source']} | Time: {node['time']}")
                        print()
                else:
                    print("Please enter a valid number")

            elif choice == "3":
                keyword = input("Please enter search keyword: ").strip()
                if keyword:
                    print(f"\nSearching for news containing '{keyword}'...")
                    query = """
                    query {
                      newsCollection(first: 100) {
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

                    result = client.execute_query(query=query)
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

            elif choice == "4":
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
