import os
import anthropic

MODEL = "claude-sonnet-5"
MAX_STEPS = 6

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

ORDERS = {
    "A1001": {"item": "Wireless Mouse", "status": "delivered", "total": 24.99},
    "A1002": {"item": "Mechanical Keyboard", "status": "in transit", "total": 89.00},
}


def look_up_order(order_id: str) -> dict:
    return ORDERS.get(order_id, {"error": f"no order found with id {order_id}"})


TOOLS = [
    {
        "name": "look_up_order",
        "description": (
            "Look up a single order by its exact order ID. Use this before "
            "discussing any order-specific detail like status or price."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    }
]

SYSTEM_PROMPT = (
    "You are a support agent for an online store. You can look up orders by ID. "
    "You cannot issue refunds, cancellations, or any other action yet. "
    "Reply in plain text for a terminal: no Markdown, no asterisks, no bullet symbols."
)


def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    for _ in range(MAX_STEPS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(
                block.text for block in response.content if block.type == "text"
            )

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "look_up_order":
                result = look_up_order(**block.input)
            else:
                result = {"error": f"unknown tool {block.name}"}
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": str(result)}
            )
        messages.append({"role": "user", "content": tool_results})

    return "stopped: exceeded MAX_STEPS without a final answer"


if __name__ == "__main__":
    print(run_agent("Hi, can you check on order A1001?"))
