# MCP Server

pykiwoom은 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 서버를 제공하여 Claude Desktop 등 AI 어시스턴트에서 키움 API를 직접 사용할 수 있습니다.

## 설치

```bash
pip install pykiwoom[mcp]
```

## Claude Desktop 설정

`claude_desktop_config.json`에 추가:

```json
{
    "mcpServers": {
        "kiwoom": {
            "command": "pykiwoom-mcp",
            "env": {
                "KIWOOM_APPKEY": "your_app_key",
                "KIWOOM_SECRETKEY": "your_secret_key"
            }
        }
    }
}
```

모의투자 서버를 사용하려면 `KIWOOM_MOCK: "true"`를 추가합니다.

## 제공 도구

| Tool | Description |
|------|-------------|
| `get_stock_price` | 주식 현재가 조회 |
| `get_balance` | 잔고 조회 |
| `get_portfolio_summary` | 포트폴리오 요약 |
| `place_order` | 매수/매도 주문 |
| `get_order_book` | 호가 조회 |
| `get_chart` | 차트 데이터 조회 |
| `get_execution_history` | 체결내역 조회 |

## Anthropic SDK 연동

MCP 도구를 Anthropic Python SDK와 직접 사용할 수 있습니다:

```python
from pykiwoom.mcp.helpers import get_anthropic_tools, execute_tool

tools = get_anthropic_tools()

# Anthropic API 호출 시 tools 파라미터로 전달
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    messages=[{"role": "user", "content": "삼성전자 현재가 알려줘"}],
)

# Tool 실행
for block in response.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
```

## MCP Client

프로그래밍 방식으로 MCP 서버에 연결할 수 있습니다:

```python
from pykiwoom.mcp.helpers import KiwoomMCPClient

async with KiwoomMCPClient() as mcp_client:
    tools = await mcp_client.list_tools()
    result = await mcp_client.call_tool("get_stock_price", {"stock_code": "005930"})
```
