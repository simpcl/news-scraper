#!/usr/bin/env python3
"""
PostgreSQL GraphQL MCP Tool
Generic PostgreSQL GraphQL API client that accesses database through HTTP RESTful API + GraphQL protocol
"""

import json
import urllib.request
import urllib.error
import os
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Try to load .env file from current directory and parent directories
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        # Try parent directory
        parent_env_path = Path.cwd().parent / ".env"
        if parent_env_path.exists():
            load_dotenv(parent_env_path)
            print(f"Loaded environment variables from {parent_env_path}")
except ImportError:
    print("Warning: python-dotenv not installed. .env file auto-loading is disabled.")
    print("To enable .env support, install: pip install python-dotenv")


# GraphQL API Configuration
GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT", "http://127.0.0.1:9782/rpc/graphql")
BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME", "")
BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD", "")

class GraphQLClient:
    """PostgreSQL GraphQL API Client"""

    def __init__(self, endpoint: str = GRAPHQL_ENDPOINT):
        self.endpoint = endpoint

    def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute GraphQL query

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name

        Returns:
            Query result dictionary
        """
        payload = {
            "query": query,
            "variables": variables or {},
            "operationName": operation_name,
        }

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Add Basic Authentication if credentials are provided
        if BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD:
            credentials = f"{BASIC_AUTH_USERNAME}:{BASIC_AUTH_PASSWORD}"
            encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {encoded_credentials}"

        try:
            # Prepare request data
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.endpoint, data=data, headers=headers, method="POST"
            )

            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    error_data = response.read().decode("utf-8")
                    raise Exception(f"HTTP Error: {response.status} - {error_data}")

                # Parse response
                response_data = response.read().decode("utf-8")
                result = json.loads(response_data)

                # Check GraphQL errors
                if "errors" in result:
                    error_msg = "; ".join(
                        [
                            err.get("message", "Unknown Error")
                            for err in result["errors"]
                        ]
                    )
                    raise Exception(f"GraphQL Error: {error_msg}")

                return result

        except urllib.error.URLError as e:
            raise Exception(f"Network request error: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing error: {str(e)}")


# Common MCP Tool Functions


def graphql_query(
    query: str, variables: Optional[str] = None, operation_name: Optional[str] = None
) -> str:
    """
    Execute generic GraphQL query

    Args:
        query: GraphQL query string
        variables: JSON format variables string (optional)
        operation_name: Operation name (optional)

    Returns:
        JSON format query result
    """
    try:
        # Parse variables string
        parsed_variables = None
        if variables and variables.strip():
            try:
                parsed_variables = json.loads(variables)
            except json.JSONDecodeError:
                return json.dumps(
                    {"error": "Variables JSON format error"},
                    ensure_ascii=False,
                    indent=2,
                )

        # Execute query
        client = GraphQLClient()
        result = client.execute_query(
            query=query, variables=parsed_variables, operation_name=operation_name
        )

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)


def introspection_query() -> str:
    """
    Execute GraphQL introspection query to get database schema information

    Returns:
        JSON format GraphQL schema
    """
    query = """
    query IntrospectionQuery {
      __schema {
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
          kind
          name
          description
          fields {
            name
            type {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
    """

    try:
        client = GraphQLClient()
        result = client.execute_query(query=query)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)


def list_tables() -> str:
    """
    List all available tables/collections

    Returns:
        JSON format table list
    """
    query = """
    query ListTables {
      __schema {
        queryType {
          fields {
            name
            description
            type {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
    """

    try:
        client = GraphQLClient()
        result = client.execute_query(query=query)

        # Extract query field names (usually correspond to database tables)
        if "data" in result and "__schema" in result["data"]:
            query_fields = result["data"]["__schema"]["queryType"]["fields"]
            tables = []

            for field in query_fields:
                # Filter out GraphQL built-in fields
                field_name = field["name"]
                if not field_name.startswith("__"):
                    table_name = ""
                    if field_name.endswith("Collection"):
                        table_name = field_name[:-10]
                        tables.append(
                            {
                                "name": table_name,
                                "type": "collection",
                                "description": field.get("description", ""),
                            }
                        )

            return json.dumps(
                {"tables": tables, "total": len(tables)}, ensure_ascii=False, indent=2
            )

        return result

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)


def get_table_info(table_name: str) -> str:
    """
    Get detailed information for a specified table

    Args:
        table_name: Table name

    Returns:
        JSON format table structure information
    """
    # Get field information through introspection query first
    introspection_query_str = f"""
    query GetTableInfo {{
      __type(name: "{table_name}") {{
        kind
        name
        description
        fields {{
          name
          type {{
            kind
            name
            ofType {{
              kind
              name
              ofType {{
                kind
                name
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        client = GraphQLClient()
        result = client.execute_query(query=introspection_query_str)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)


def execute_collection_query(
    collection_name: str,
    fields: Optional[List[str]] = None,
    first: int = 10,
    filter: Optional[Dict[str, Any]] = None,
    order_by: Optional[Dict[str, str]] = None,
) -> str:
    """
    Execute collection query (generic query method)

    Args:
        collection_name: Collection/table name
        fields: List of fields to return (optional)
        first: Number of records to return (default 10). If > 30, automatically paginates.
        filter: GraphQL filter condition as dict, e.g. {"id": {"eq": 1}} or {"title": {"ilike": "%keyword%"}} (optional)
        order_by: Sorting condition as dict, e.g. {"time": "DescNullsLast"} (optional)

    Returns:
        JSON format query result
    """
    # Build basic query
    if fields is None:
        fields = ["id"]
    else:
        fields += ["id"]
    fields_str = "\n        ".join(fields)

    # Build query arguments
    query_args = []
    base_variables = {}

    # Filter and orderBy are used in all requests
    if filter:
        filter_type = f"{collection_name.capitalize()}Filter"
        query_args.append(f"$filter: {filter_type}")
        base_variables["filter"] = filter

    if order_by:
        order_by_type = f"{collection_name.capitalize()}OrderBy"
        query_args.append(f"$orderBy: {order_by_type}")
        base_variables["orderBy"] = order_by

    query_args.append("$first: Int")
    query_args.append("$after: String")

    client = GraphQLClient()

    # Automatic pagination when first > 30
    all_edges = []
    current_after = None
    remaining = first
    page_size = 30

    try:
        while remaining > 0:
            # Determine the number of records to fetch in this batch
            current_first = min(remaining, page_size)

            variables = base_variables.copy()
            variables["first"] = current_first
            if current_after:
                variables["after"] = current_after

            collection_args = ["first: $first"]
            if current_after:
                collection_args.append("after: $after")
            if filter:
                collection_args.append("filter: $filter")
            if order_by:
                collection_args.append("orderBy: $orderBy")

            query = f"""
            query Query{collection_name.capitalize()}({", ".join(query_args)}) {{
              {collection_name}Collection({", ".join(collection_args)}) {{
                edges {{
                  node {{
                    {fields_str}
                  }}
                  cursor
                }}
                pageInfo {{
                  hasNextPage
                  hasPreviousPage
                  endCursor
                  startCursor
                }}
              }}
            }}
            """

            result = client.execute_query(query=query, variables=variables)

            # Check for errors
            if "errors" in result:
                return result
                # return json.dumps(result, ensure_ascii=False, indent=2)

            # Extract edges and pageInfo
            if "data" not in result:
                return result
                # return json.dumps(result, ensure_ascii=False, indent=2)

            collection_key = f"{collection_name}Collection"
            if collection_key not in result["data"]:
                return result
                # return json.dumps(result, ensure_ascii=False, indent=2)

            collection_data = result["data"][collection_key]
            edges = collection_data.get("edges", [])
            page_info = collection_data.get("pageInfo", {})

            # Add edges to result
            all_edges.extend(edges)
            remaining -= len(edges)

            # Check if we need to continue pagination
            has_next_page = page_info.get("hasNextPage", False)
            if not has_next_page or remaining <= 0:
                break

            # Update cursor for next request
            current_after = page_info.get("endCursor")
            if not current_after:
                break

        # Build final result
        final_result = {
            "data": {
                collection_key: {
                    "edges": all_edges,
                    "pageInfo": {
                        "hasNextPage": remaining > 0,
                        "hasPreviousPage": False,
                        "totalFetched": len(all_edges),
                    }
                }
            }
        }
        return final_result
        # return json.dumps(final_result, ensure_ascii=False, indent=2)

    except Exception as e:
        return {"error": str(e)}
        # return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
