#!/usr/bin/env python3

import json

from pg_graphql import execute_collection_query

def paged_query_news():
    print("=== Method 1: Manual Pagination (using execute_collection_query) ===")
    print("Fetching first 3 pages of data, 3 records per page\n")

    all_pages_data = []
    current_cursor = None
    page_size = 3
    total_pages = 3

    for page_num in range(1, total_pages + 1):
        print(f"📄 Fetching page {page_num}...")

        try:
            # Call execute_collection_query
            result_json = execute_collection_query(
                collection_name="news",
                first=page_size,
                after=current_cursor,
            )

            result = json.loads(result_json)

            # Check for errors
            if "error" in result:
                print(f"✗ Page {page_num} query failed: {result['error']}")
                break

            # Extract data
            if "data" in result:
                collection = result["data"]["newsCollection"]
                edges = collection["edges"]
                page_info = collection["pageInfo"]

                print(f"✓ Page {page_num}: Retrieved {len(edges)} records")

                # Display current page record IDs
                record_ids = [edge["node"]["id"] for edge in edges]
                print(f"   Record IDs: {record_ids}")

                # Save current page data
                all_pages_data.append(
                    {
                        "page": page_num,
                        "records": edges,
                        "pageInfo": page_info,
                    }
                )

                # Check if there's a next page
                has_next = page_info.get("hasNextPage", False)
                end_cursor = page_info.get("endCursor")

                if not has_next or not end_cursor:
                    print(f"   No more pages available")
                    break

                # Update cursor for next page fetch
                current_cursor = end_cursor
                print(f"   Next page cursor: {end_cursor}\n")

        except Exception as e:
            print(f"✗ Page {page_num} query failed: {str(e)}")
            break

    print(f"\n✅ Total pages retrieved: {len(all_pages_data)}")
    print(f"   Total records: {sum(len(page['records']) for page in all_pages_data)} records\n")


def single_page_query_news():
    print("=== Method 2: Single Page Query (fetching first page) ===")
    print("Fetching first page data, 3 records total\n")

    try:
        # Don't pass after parameter to get first page
        result_json = execute_collection_query(
            collection_name="news",
            first=3,
        )

        result = json.loads(result_json)

        if "error" in result:
            print(f"✗ Query failed: {result['error']}")
            return

        if "data" in result:
            collection = result["data"]["newsCollection"]
            edges = collection["edges"]
            page_info = collection["pageInfo"]

            print(f"✅ Retrieved {len(edges)} records")
            print(f"   Has next page: {page_info.get('hasNextPage', False)}")
            print(f"   End cursor: {page_info.get('endCursor', 'N/A')}")

            # Display record details
            print("\n   Record Details:")
            for i, edge in enumerate(edges, 1):
                node = edge["node"]
                cursor = edge.get("cursor", "N/A")
                print(f"   {i}. ID: {node['id']}, Cursor: {cursor}")

    except Exception as e:
        print(f"✗ Query failed: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Pagination News Query From PostgreSQL GraphQL ")
    print("=" * 60)
    print()

    # 1: Manual pagination
    paged_query_news()

    print("\n" + "=" * 60 + "\n")

    # 2: Single page query
    single_page_query_news()

    print("\n" + "=" * 60)

    print("Program completed!")
    print("=" * 60)
