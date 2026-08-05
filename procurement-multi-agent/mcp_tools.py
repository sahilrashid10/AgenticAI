from autogen_ext.tools.mcp import (
    StdioServerParams,
    mcp_server_tools,
)

import asyncio
import sys
from pathlib import Path


async def get_mcp_tools():

    server_script = Path(__file__).with_name("mcp_server.py")

    server = StdioServerParams(
        command=sys.executable,
        args=[str(server_script)],
    )

    tools = await mcp_server_tools(server)

    return tools