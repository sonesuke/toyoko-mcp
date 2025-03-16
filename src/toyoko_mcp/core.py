import mcp.types as types
from mcp.server import Server
from playwright.async_api import async_playwright, Playwright, Page
import logging

app = Server("Toyoko server")

# Keep Playwright as a global variable for efficient browser operations
playwright: Playwright | None = None

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

URLs = {"top": "https://www.toyoko-inn.com/corporation?lcl_id=ja"}


async def initialize_playwright() -> None:
    """
    Initialize Playwright and set it to the global variable.
    """
    global playwright
    if playwright is None:
        logger.debug("Initializing Playwright...")
        playwright = await async_playwright().start()
        logger.debug("Playwright initialized.")


async def shutdown_playwright() -> None:
    """
    Shut down Playwright and release resources.
    """
    global playwright
    if playwright is not None:
        await playwright.stop()
        playwright = None


@app.list_tools()  # type: ignore
async def list_tools() -> list[types.Tool]:
    """
    Return a list of available tools.
    """
    return []


@app.call_tool()  # type: ignore
async def login(
    name: str, arguments: dict[str, str]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Perform the login process and return the result.
    """
    if playwright is None:
        raise RuntimeError(
            "Playwright is not initialized. Call initialize_playwright() first."
        )

    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(URLs["top"])

    # Close the browser context and release resources
    await context.close()
    await browser.close()

    return [
        types.TextContent(type="text", text="some function is executed successfully")
    ]


async def save_dom(page: Page, path: str) -> None:
    """
    Save the DOM of the page to a file.
    """
    dom_content = await page.content()
    with open(path, "w", encoding="utf-8") as file:
        file.write(dom_content)
    logger.debug(f"DOM content saved to {path}")
