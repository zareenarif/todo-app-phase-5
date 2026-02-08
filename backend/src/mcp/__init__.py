"""
MCP (Model Context Protocol) server package.
Exposes stateless task operation tools for the AI agent.
"""
from mcp.server.fastmcp import FastMCP

# Create the MCP server instance (shared across tools module)
mcp_server = FastMCP(
    name="todo-mcp-server",
)
