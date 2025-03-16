import mcp.types as types
from mcp.server import Server
from playwright.async_api import (
    async_playwright,
    Playwright,
    Page,
    Browser,
    BrowserContext,
)
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = Server("Toyoko server")

# Keep Playwright as a global variable for efficient browser operations
URLs = {"top": "https://www.toyoko-inn.com/corporation?lcl_id=ja"}
playwright: Playwright | None = None


class Context:
    browser: Browser | None = None
    context: BrowserContext | None = None
    main_page: Page | None = None

    def __init__(self, browser: Browser, context: BrowserContext, main_page: Page):
        self.browser = browser
        self.context = context
        self.main_page = main_page

    def close(self) -> None:
        if self.context is not None:
            self.context.close()
        if self.browser is not None:
            self.browser.close()


context: Context | None = None


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
    global context
    if context is not None:
        context.close()
    global playwright
    if playwright is not None:
        await playwright.stop()
        playwright = None


@app.list_tools()  # type: ignore
async def list_tools() -> list[types.Tool]:
    """
    Return a list of available tools.
    """
    return [
        types.Tool(
            name="login",
            description="Login to the Toyoko Inn(東横イン) website",
            inputSchema={},
        )
    ]


@app.call_tool()  # type: ignore
async def login(
    name: str, arguments: dict[str, str]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Log in to the Toyoko Inn website.
    """
    if playwright is None:
        raise RuntimeError(
            "Playwright is not initialized. Call initialize_playwright() first."
        )

    # Retrieve values from environment variables
    corporate_id = os.getenv("CORPORATE_ID")
    if not corporate_id:
        raise ValueError("Environment variable 'CORPORATE_ID' is not set.")

    user_email = os.getenv("USER_EMAIL")
    if not user_email:
        raise ValueError("Environment variable 'USER_EMAIL' is not set.")

    user_password = os.getenv("USER_PASSWORD")
    if not user_password:
        raise ValueError("Environment variable 'USER_PASSWORD' is not set.")

    # Open the top page and click the login link
    headless_mode = os.environ.get("TOYOKO_MCP_HEADLESS", "true").lower() == "true"
    browser = await playwright.chromium.launch(headless=headless_mode)
    browser_context = await browser.new_context(
        locale="ja-JP",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        timezone_id="Asia/Tokyo",
    )
    top_page = await browser_context.new_page()
    await top_page.goto(URLs["top"])
    async with top_page.expect_popup() as main_page_info:
        await top_page.get_by_role(
            "link",
            name="東横INNクラブ コーポレートビジネス会員の方（契約企業様） ログイン",
        ).click()

    # Fill the login form with values from environment variables
    main_page = await main_page_info.value

    await main_page.get_by_role("textbox", name="法人ID").fill(corporate_id)
    await main_page.get_by_role(
        "textbox", name="ユーザーID、又はユーザーメールアドレス"
    ).fill(user_email)
    await main_page.get_by_role("textbox", name="ユーザーパスワード").fill(
        user_password
    )
    await main_page.get_by_role("button", name="ログイン").click()

    global context
    context = Context(browser, browser_context, main_page)

    return [types.TextContent(type="text", text="Login successfully")]


async def save_dom(page: Page, path: str) -> None:
    """
    Save the DOM of the page to a file.
    """
    dom_content = await page.content()
    with open(path, "w", encoding="utf-8") as file:
        file.write(dom_content)
    logger.debug(f"DOM content saved to {path}")
