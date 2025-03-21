set dotenv-load

install:
    curl -LsSf https://astral.sh/uv/install.sh | sh
    pip install pre-commit

test: 
    uv run pytest --cov=src -s

format:
    uv run ruff format
    uv run docformatter --in-place --config ./pyproject.toml src tests

check: 
    pre-commit run -a

clean:
    uv cache clean

goose:
    export LANGFUSE_SECRET_KEY=$LANGFUSE_SECRET_KEY
    export LANGFUSE_PUBLIC_KEY=$LANGFUSE_PUBLIC_KEY
    export LANGFUSE_HOST=$LANGFUSE_HOST
    goose session

inspector:
    npx @modelcontextprotocol/inspector uv --directory . run toyoko_mcp_cli
