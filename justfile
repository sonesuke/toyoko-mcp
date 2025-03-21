install:
    curl -LsSf https://astral.sh/uv/install.sh | sh
    pip install pre-commit

test: 
    uv run pytest --cov=src -s

format:
    uv run ruff format
    uv run docformatter --in-place --config ./pyproject.toml src tests

format_readme:
    prettier --write README.md

check: 
    pre-commit run -a

run:
    uv sync
    uv run cli
