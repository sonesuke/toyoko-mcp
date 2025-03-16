import pytest
from toyoko_mcp.core import list_tools


@pytest.mark.asyncio  # type: ignore
async def test_list_tools() -> None:
    result = await list_tools()
    assert len(result) == 0
