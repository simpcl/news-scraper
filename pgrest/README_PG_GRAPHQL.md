# PostgreSQL GraphQL MCP Tool

Generic PostgreSQL GraphQL API client that accesses database through HTTP RESTful API + GraphQL protocol.

## Features

- **GraphQL Query Execution**: Execute arbitrary GraphQL queries with variables
- **Introspection Support**: Query database schema and table information
- **Automatic Pagination**: Automatically handle pagination when fetching large datasets (>30 records)
- **Basic Authentication**: Support for HTTP Basic Authentication
- **Environment Configuration**: Flexible configuration via environment variables

## Installation

### Requirements

```bash
pip install python-dotenv
```

### Environment Variables

Create a `.env` file in your project directory:

```bash
# GraphQL API Endpoint
GRAPHQL_ENDPOINT=http://127.0.0.1:9782/rpc/graphql

# Basic Authentication (optional)
BASIC_AUTH_USERNAME=your_username
BASIC_AUTH_PASSWORD=your_password
```

## Usage

### GraphQL Client

Basic usage of the `GraphQLClient` class:

```python
from pgrest.pg_graphql import GraphQLClient

# Initialize client
client = GraphQLClient()

# Execute query
query = """
    query GetNews {
        newsCollection(first: 10) {
            edges {
                node {
                    id
                    title
                    url
                }
            }
        }
    }
"""

result = client.execute_query(query)
print(result)
```

### MCP Tool Functions

#### 1. Generic GraphQL Query

Execute any GraphQL query with optional variables:

```python
from pgrest.pg_graphql import graphql_query

query = """
    query GetNewsByDate($date: String!) {
        newsCollection(filter: {date: {eq: $date}}) {
            edges {
                node {
                    id
                    title
                }
            }
        }
    }
"""

variables = json.dumps({"date": "2024-01-01"})
result = graphql_query(query, variables=variables)
```

#### 2. Introspection Query

Get complete database schema information:

```python
from pgrest.pg_graphql import introspection_query

schema = introspection_query()
print(schema)
```

#### 3. List Tables

List all available tables/collections:

```python
from pgrest.pg_graphql import list_tables

tables = list_tables()
# Returns: {"tables": [{"name": "news", "type": "collection", ...}], "total": N}
```

#### 4. Get Table Info

Get detailed structure information for a specific table:

```python
from pgrest.pg_graphql import get_table_info

table_info = get_table_info("News")
print(table_info)
```

#### 5. Execute Collection Query

Query collections with filtering, sorting, and automatic pagination:

```python
from pgrest.pg_graphql import execute_collection_query

# Basic query
result = execute_collection_query(
    collection_name="news",
    fields=["title", "url", "time"],
    first=10
)

# Query with filtering
result = execute_collection_query(
    collection_name="news",
    fields=["title", "url", "time"],
    filter={"title": {"ilike": "%AI%"}},
    first=50  # Automatically paginates
)

# Query with sorting
result = execute_collection_query(
    collection_name="news",
    fields=["title", "url", "time"],
    order_by={"time": "DescNullsLast"},
    first=20
)

# Combined query
result = execute_collection_query(
    collection_name="news",
    fields=["title", "url", "time", "content"],
    first=100,
    filter={"time": {"gte": "2024-01-01"}},
    order_by={"time": "Desc"}
)
```

## API Reference

### GraphQLClient

#### `__init__(endpoint: str = GRAPHQL_ENDPOINT)`

Initialize GraphQL client with custom endpoint.

#### `execute_query(query: str, variables: Optional[Dict[str, Any]] = None, operation_name: Optional[str] = None) -> Dict[str, Any]`

Execute GraphQL query with optional variables and operation name.

**Parameters:**
- `query`: GraphQL query string
- `variables`: Query variables dictionary
- `operation_name`: Operation name for query

**Returns:**
- Query result dictionary

### Tool Functions

#### `graphql_query(query: str, variables: Optional[str] = None, operation_name: Optional[str] = None) -> str`

Execute generic GraphQL query.

**Parameters:**
- `query`: GraphQL query string
- `variables`: JSON format variables string (optional)
- `operation_name`: Operation name (optional)

**Returns:**
- JSON format query result string

#### `introspection_query() -> str`

Execute GraphQL introspection query to get database schema information.

**Returns:**
- JSON format GraphQL schema string

#### `list_tables() -> str`

List all available tables/collections.

**Returns:**
- JSON format table list string

#### `get_table_info(table_name: str) -> str`

Get detailed information for a specified table.

**Parameters:**
- `table_name`: Table name

**Returns:**
- JSON format table structure information string

#### `execute_collection_query(collection_name: str, fields: Optional[List[str]] = None, first: int = 10, filter: Optional[Dict[str, Any]] = None, order_by: Optional[Dict[str, str]] = None) -> str`

Execute collection query with support for filtering, sorting, and automatic pagination.

**Parameters:**
- `collection_name`: Collection/table name
- `fields`: List of fields to return (optional, defaults to `["id"]`)
- `first`: Number of records to return (default 10). If > 30, automatically paginates
- `filter`: GraphQL filter condition as dict (optional)
  - Example: `{"id": {"eq": 1}}`
  - Example: `{"title": {"ilike": "%keyword%"}}`
- `order_by`: Sorting condition as dict (optional)
  - Example: `{"time": "DescNullsLast"}`

**Returns:**
- JSON format query result dictionary with paginated edges

**Filter Operators:**
- `eq`: Equal to
- `neq`: Not equal to
- `gt`: Greater than
- `gte`: Greater than or equal to
- `lt`: Less than
- `lte`: Less than or equal to
- `ilike`: Case-insensitive pattern matching
- `like`: Case-sensitive pattern matching
- `in`: In array
- `isNull`: Is null

**Sort Options:**
- `Asc`: Ascending
- `AscNullsFirst`: Ascending with nulls first
- `AscNullsLast`: Ascending with nulls last
- `Desc`: Descending
- `DescNullsFirst`: Descending with nulls first
- `DescNullsLast`: Descending with nulls last

## Automatic Pagination

When `first` parameter is greater than 30, the `execute_collection_query` function automatically handles pagination:

```python
# Fetch 100 records with automatic pagination
result = execute_collection_query(
    collection_name="news",
    fields=["title", "url"],
    first=100  # Will make multiple requests of 30 records each
)
```

The function will:
1. Make multiple requests with `first: 30`
2. Use the `after` cursor to get subsequent pages
3. Aggregate all edges into a single result
4. Return combined data with pagination metadata

## Error Handling

All functions return error information in JSON format:

```python
result = graphql_query("invalid query")
# Returns: {"error": "GraphQL Error: ..."}
```

Always check for errors in the response:

```python
result = execute_collection_query("news", first=10)
if "error" in result:
    print(f"Error: {result['error']}")
elif "errors" in result.get("data", {}):
    print(f"GraphQL Errors: {result['data']['errors']}")
else:
    # Process successful result
    edges = result["data"]["newsCollection"]["edges"]
```

## Examples

### Query with Multiple Filters

```python
result = execute_collection_query(
    collection_name="news",
    fields=["id", "title", "url", "time", "source"],
    first=50,
    filter={
        "and": [
            {"time": {"gte": "2024-01-01"}},
            {"time": {"lt": "2024-02-01"}},
            {"source": {"eq": "TechNews"}}
        ]
    },
    order_by={"time": "Desc"}
)
```

### Query Specific Fields

```python
result = execute_collection_query(
    collection_name="news",
    fields=["title", "url"],  # Only fetch title and url
    first=20
)
```

### Query with Variables

```python
query = """
    query SearchNews($searchTerm: String!) {
        newsCollection(
            filter: {
                or: [
                    {title: {ilike: $searchTerm}},
                    {content: {ilike: $searchTerm}}
                ]
            }
        ) {
            edges {
                node {
                    id
                    title
                    url
                }
            }
        }
    }
"""

variables = json.dumps({
    "searchTerm": "%artificial intelligence%"
})

result = graphql_query(query, variables=variables)
```

## License

This tool is part of the news-scraper project.
