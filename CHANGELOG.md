# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-05-19

### Added

- `PyKiwoom` sync client and `AsyncPyKiwoom` async client
- OAuth2 token management with automatic refresh
- Global rate limiter (5 req/s real, 1 req/s mock)
- Automatic pagination via `cont-yn`/`next-key` headers
- Domestic market API (`DomesticAPI`)
  - Price, order book, stock info, tickers
  - Balance, execution history, orderable quantity
  - Buy, sell, modify, cancel orders
  - Chart data (tick, minute, day)
- Pydantic response models (`StockPrice`, `Balance`, `OrderResult`, `ChartData`)
- MCP server for AI assistant integration (`pykiwoom-mcp`)
- CLI tool (`pykiwoom`)
- Full type annotations (PEP 561 `py.typed`)

[0.1.0]: https://github.com/Jaeminyx-Stoa/pykiwoom/releases/tag/v0.1.0
