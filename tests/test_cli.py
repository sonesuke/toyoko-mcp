from typing import AsyncGenerator
import os
from pathlib import Path
from urllib.parse import quote

import pytest
from pytest_asyncio import fixture  # Import fixture from pytest-asyncio
from toyoko_mcp.core import (
    list_tools,
    login,
    initialize_playwright,
    shutdown_playwright,
    URLs,
)

from dotenv import load_dotenv

load_dotenv()


def replace_url_to_mock() -> None:
    """
    Replaces the URL in the `URLs` dictionary with a mock file URL and sets
    environment variables for testing purposes.
    This function performs the following actions:
    1. Updates the "top" key in the `URLs` dictionary to point to a local
       mock HTML file located in the `pages` directory relative to the
       current script's directory.
    2. Sets the `CORPORATE_ID` environment variable to a mock corporate ID.
    3. Sets the `USER_EMAIL` environment variable to a mock email address.
    4. Sets the `USER_PASSWORD` environment variable to a mock password.
    Note:
    - This function is intended for use in a testing environment to simulate
      specific conditions without relying on external resources.
    - Ensure that the `URLs` dictionary is defined and accessible in the
      current scope before calling this function.
    """

    current_dir = Path(__file__).parent
    URLs["top"] = quote(f"file://{current_dir}/pages/top.html", safe=":/")
    os.environ["CORPORATE_ID"] = "B123-456789"
    os.environ["USER_EMAIL"] = "someone@example.com"
    os.environ["USER_PASSWORD"] = "1234"
    os.environ["TOYOKO_MCP_HEADLESS"] = "false"


@fixture(scope="function", autouse=True)  # type: ignore
async def setup_playwright() -> AsyncGenerator[None, None]:
    """
    Ensure Playwright is initialized and shut down properly.
    """
    replace_url_to_mock()

    await initialize_playwright()
    yield
    await shutdown_playwright()


@pytest.mark.asyncio  # type: ignore
async def test_list_tools() -> None:
    """
    Test the list_tools function.
    """
    result = await list_tools()
    assert len(result) == 1


@pytest.mark.asyncio  # type: ignore
async def test_login() -> None:
    """
    Test the login function.
    """
    result = await login("login", {})
    assert len(result) == 1
    assert result[0].type == "text"
    assert result[0].text == "Login successfully"
