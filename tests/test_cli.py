from typing import AsyncGenerator
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


@fixture(scope="function", autouse=True)  # type: ignore
async def setup_playwright() -> AsyncGenerator[None, None]:
    """
    Ensure Playwright is initialized and shut down properly.
    """
    current_dir = Path(__file__).parent
    URLs["top"] = quote(f"file://{current_dir}/pages/top.html", safe=":/")

    await initialize_playwright()
    yield
    await shutdown_playwright()


@pytest.mark.asyncio  # type: ignore
async def test_list_tools() -> None:
    """
    Test the list_tools function.
    """
    result = await list_tools()
    assert len(result) == 0


@pytest.mark.asyncio  # type: ignore
async def test_login() -> None:
    """
    Test the login function.
    """
    result = await login("login", {"key": "value"})
    assert len(result) == 1
    assert result[0].type == "text"
    assert result[0].text == "some function is executed successfully"
