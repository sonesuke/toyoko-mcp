import asyncio
from toyoko_mcp.core import app
from mcp.server.stdio import stdio_server


# pragma: no cover
async def main() -> None:
    async with stdio_server() as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())


# pragma: no cover
def run_main() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
