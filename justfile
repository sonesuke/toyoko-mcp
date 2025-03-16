install:
    curl -LsSf https://astral.sh/uv/install.sh | sh
    pip install pre-commit

test: 
    uv run pytest --cov=src -s

check: 
    pre-commit run -a

run:
    uv sync
    uv run cli