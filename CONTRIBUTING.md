# Contributing to pykiwoom

## Development Setup

```bash
git clone https://github.com/Jaeminyx-Stoa/pykiwoom.git
cd pykiwoom
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Quality

```bash
ruff check src/ tests/     # lint
ruff format src/ tests/     # format
mypy src/pykiwoom/ --ignore-missing-imports  # type check
```

## Pull Request Guidelines

1. Fork the repository and create a feature branch from `main`
2. Add tests for new functionality
3. Ensure all tests pass and linting is clean
4. Write a clear PR description explaining the change

## Commit Messages

Use concise, descriptive commit messages:
- `Add <feature>` for new features
- `Fix <issue>` for bug fixes
- `Update <target>` for enhancements

## Architecture

```
src/pykiwoom/
├── auth.py          # OAuth2 token management
├── ratelimit.py     # Global rate limiter
├── http.py          # HTTP client with pagination
├── client.py        # PyKiwoom / AsyncPyKiwoom
├── api/
│   └── domestic.py  # Domestic market API
├── models/          # Pydantic response models
├── mcp/             # MCP server for AI assistants
└── cli.py           # CLI tool
```

## Reporting Issues

Open an issue at https://github.com/Jaeminyx-Stoa/pykiwoom/issues with:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
