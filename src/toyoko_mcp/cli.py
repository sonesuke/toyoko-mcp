import asyncio
from toyoko_mcp.core import app, initialize_playwright, shutdown_playwright
from mcp.server.stdio import stdio_server


# pragma: no cover
async def main() -> None:
    await initialize_playwright()
    try:
        async with stdio_server() as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())
    finally:
        await shutdown_playwright()

# pragma: no cover
def run_main() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
