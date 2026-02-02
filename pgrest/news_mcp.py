#!/usr/bin/env python3

from fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("News Query MCP With PostgreSQL GraphQL Client")


if __name__ == "__main__":
    # Run MCP server
    mcp.run()