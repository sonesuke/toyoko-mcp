import mcp.types as types
from mcp.server import Server


app = Server("Toyoko server")


@app.list_tools()  # type: ignore
async def list_tools() -> list[types.Tool]:
    return []


@app.call_tool()  # type: ignore
async def some_function(
    name: str, arguments: dict[str, str]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    return [
        types.TextContent(type="text", text="some function is executed successfully")
    ]
