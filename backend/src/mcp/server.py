"""
MCP Server setup.
Imports tools to register them, then exposes the configured server.
"""
from src.mcp import mcp_server  # noqa: F401
from src.mcp import tools  # noqa: F401 - registers tools on mcp_server
