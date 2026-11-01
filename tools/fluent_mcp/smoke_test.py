"""Start the MCP server over stdio and list its tools (no Fluent needed)."""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).with_name("ansys_fluent_mcp.py"))])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"{len(tools.tools)} tools:", ", ".join(t.name for t in tools.tools))
            res = await session.call_tool("fluent_status", {})
            print(res.content[0].text)


asyncio.run(main())
