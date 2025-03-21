from typing import Any, Dict, List, Optional
import mcp.types as types
from mcp.server import Server
from playwright.async_api import (
    async_playwright,
    Playwright,
    Page,
    Browser,
    BrowserContext,
)
import json
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = Server(
    name="Toyoko-Inn server",
    version="0.1.0",
    instructions="""
This server provides tools to interact with the Toyoko-Inn website.
    """,
)

# Keep Playwright as a global variable for efficient browser operations
URLs = {"top": "https://www.toyoko-inn.com/corporation?lcl_id=ja"}
playwright: Optional[Playwright] = None


class Context:
    """
    Context class to manage browser, context, and page.
    """

    browser: Optional[Browser] = None
    context: Optional[BrowserContext] = None
    main_page: Optional[Page] = None

    def __init__(self, browser: Browser, context: BrowserContext, main_page: Page):
        """
        Initialize the context with browser, context, and main page.
        """
        self.browser = browser
        self.context = context
        self.main_page = main_page

    async def close(self) -> None:
        """
        Close the browser context and browser.
        """
        if self.context is not None:
            await self.context.close()
        if self.browser is not None:
            await self.browser.close()


context: Optional[Context] = None


async def initialize_playwright() -> None:
    """
    Initialize Playwright and set it to the global variable.
    """
    global context
    context = None
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
        await context.close()
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
        ),
        types.Tool(
            name="list_region",
            description="List the regions available for booking in Toyoko Inn(東横イン)",
            inputSchema={},
        ),
        types.Tool(
            name="list_hotel",
            description="List the hotels available for booking in Toyoko Inn(東横イン)",
            inputSchema={
                "properties": {
                    "region_id": {"type": "string", "description": "ID of the region"},
                },
                "required": ["region_id"],
            },
        ),
        types.Tool(
            name="is_available_room",
            description="List the rooms available for booking in Toyoko Inn(東横イン)",
            inputSchema={
                "properties": {
                    "region_id": {"type": "string", "description": "ID of the region"},
                    "hotel_id": {"type": "string", "description": "ID of the hotel"},
                    "month": {"type": "string", "description": "Month of the booking"},
                    "day": {"type": "string", "description": "Day of the booking"},
                    "nights": {"type": "integer", "description": "Number of nights"},
                },
                "required": ["region_id", "hotel_id", "month", "day", "nights"],
            },
        ),
    ]


@app.call_tool()  # type: ignore
async def call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Call the appropriate tool function based on the 'name' argument.
    """
    if name == "login":
        return await login(name, arguments)
    elif name == "list_region":
        return await list_region(name, arguments)
    elif name == "list_hotel":
        return await list_hotel(name, arguments)
    elif name == "is_available_room":
        return await is_available_room(name, arguments)
    else:
        raise ValueError(f"Tool '{name}' not found.")


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
    async with main_page.expect_navigation():
        await main_page.get_by_role("button", name="ログイン").click()

    global context
    context = Context(browser, browser_context, main_page)

    return [types.TextContent(type="text", text="Login successfully")]


async def get_select_options(page: Page, select_selector: str) -> list[dict[str, str]]:
    """
    Get all options from a select element.
    """
    options = await page.query_selector_all(f"{select_selector} > option")
    options_list = []
    for option in options:
        value = await option.get_attribute("value")
        text = await option.inner_text()
        options_list.append({"value": value.strip(), "text": text.strip()})
    return options_list


async def list_region(
    name: str, arguments: dict[str, int]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    List the regions available for booking in Toyoko Inn(東横イン).
    """

    global context
    if context is None:
        await login("login", {})

    if context is None:
        raise RuntimeError("Failed to log in.")

    page = context.main_page
    # <option>要素を全て取得
    options = await get_select_options(page, "#sel_area")
    result_dict = [
        {"id": option["value"], "region": option["text"]}
        for option in options
        if option["value"] != ""
    ]

    return [
        types.TextContent(type="text", text=json.dumps(result_dict, ensure_ascii=False))
    ]


async def list_hotel(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    List the hotels available for booking in Toyoko Inn(東横イン).
    """

    global context
    if context is None:
        await login("login", {})

    if context is None or context.main_page is None:
        raise RuntimeError("Failed to log in or main page is not available.")

    region_id = arguments.get("region_id")
    if region_id is None:
        raise ValueError("Argument 'region_id' is required.")

    page = context.main_page

    # Ensure the element with label "行先" exists
    region = page.get_by_label("行先")
    if region is None:
        raise ValueError("Element with label '行先' not found.")

    await region.select_option(region_id)
    options = await get_select_options(page, "#sel_htl")
    result_dict = [
        {"id": option["value"], "hotel": option["text"]}
        for option in options
        if option["value"] != ""
    ]

    return [
        types.TextContent(type="text", text=json.dumps(result_dict, ensure_ascii=False))
    ]


async def is_available_room(
    name: str, arguments: dict[str, str]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    List the rooms available for booking in Toyoko Inn(東横イン).
    """

    global context
    if context is None:
        await login("login", {})

    if context is None or context.main_page is None:
        raise RuntimeError("Failed to log in or main page is not available.")
    page = context.main_page

    region_id = arguments.get("region_id")
    if region_id is None:
        raise ValueError("Argument 'region_id' is required.")
    region = page.get_by_label("行先")
    if region is None:
        raise ValueError("Element with label '行先' not found.")
    await region.select_option(region_id)

    hotel_id = arguments.get("hotel_id")
    if hotel_id is None:
        raise ValueError("Argument 'hotel_id' is required.")
    hotel = page.locator("#sel_htl")
    if hotel is None:
        raise ValueError("Element with Id '#sel_htl' not found.")
    await hotel.select_option(hotel_id)
    nights = arguments.get("nights")
    if nights is None:
        raise ValueError("Argument 'nights' is required.")
    await page.get_by_label("泊数").select_option(str(nights))

    month = arguments.get("month")
    if month is None:
        raise ValueError("Argument 'month' is required.")
    month = str(month).zfill(2)

    day = arguments.get("day")
    if day is None:
        raise ValueError("Argument 'day' is required.")
    day = str(day).zfill(2)

    year = datetime.now().year

    # Adjust the year if the specified date has already passed
    specified_date = datetime(year, int(month), int(day))
    if specified_date < datetime.now():
        year += 1

    await page.evaluate(
        f"""
        () => {{
            const datepicker = document.querySelector('#datepicker');
            datepicker.value = '{year}-{month}-{day}';
            const event = new Event('change', {{ bubbles: true }});
            datepicker.dispatchEvent(event);
        }}
    """
    )

    # Specify the room type and smoking preference
    await page.get_by_text("シングルルーム").click()
    await page.get_by_text("禁煙", exact=True).click()

    await page.get_by_role("button", name="この条件でホテルを探す").click()

    reserve = page.get_by_role("button", name="予約")

    if reserve is None:
        return [types.TextContent(type="text", text="No rooms available")]

    return [types.TextContent(type="text", text="Rooms available")]


async def save_dom(page: Page, path: str) -> None:
    """
    Save the DOM of the page to a file.
    """
    dom_content = await page.content()
    with open(path, "w", encoding="utf-8") as file:
        file.write(dom_content)
    logger.debug(f"DOM content saved to {path}")
