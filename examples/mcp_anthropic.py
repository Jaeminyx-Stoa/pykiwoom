"""Using pykiwoom MCP tools with the Anthropic SDK."""

import anthropic

from pykiwoom.mcp.helpers import execute_tool, get_anthropic_tools

client = anthropic.Anthropic()
tools = get_anthropic_tools()

messages = [{"role": "user", "content": "삼성전자 현재가 알려줘"}]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=tools,
    messages=messages,
)

# Agentic tool-use loop
while response.stop_reason == "tool_use":
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": result}
            )

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        tools=tools,
        messages=messages,
    )

# Final text response
for block in response.content:
    if hasattr(block, "text"):
        print(block.text)
