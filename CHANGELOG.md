# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **OAuth2 token request now sends a JSON body.** It previously used
  `application/x-www-form-urlencoded`, which the Kiwoom REST API rejects with
  HTTP 415 (`UNSUPPORTED_MEDIA_TYPE`) — token issuance failed against the live
  REAL/MOCK servers despite the mocked unit tests passing.
- **Authentication failures are now raised as `TokenError`.** Kiwoom returns
  HTTP 200 with `return_code != 0` (e.g. `3`) on bad credentials; the client
  used to raise a bare `KeyError` looking up the absent `token` field.
- Token expiry now parses Kiwoom's `expires_dt` (`YYYYMMDDHHMMSS`) when present,
  falling back to `expires_in` seconds, then a 24h default.

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
