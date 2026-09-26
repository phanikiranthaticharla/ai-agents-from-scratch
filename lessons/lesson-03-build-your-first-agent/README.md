# Lesson 3 — Build Your First Agent

📺 Video: [link coming soon]

**MiniDesk v0**: a support agent with exactly one capability, looking up an order by its ID.
No refunds, nothing that spends money. It exists to make one thing concrete: **the agent loop**.

## What's in `minidesk_v0.py`

| Piece | Lines | What it is |
|---|---|---|
| `ORDERS` | 9–12 | A small dictionary that mimics a real order database |
| `look_up_order()` | 15–16 | **The tool, part one:** the function that does the actual work |
| `TOOLS` | 19–32 | **The tool, part two:** the schema, a description written for the model |
| `SYSTEM_PROMPT` | 34–38 | Instructions, passed in their own slot (not inside `messages`) |
| `run_agent()` | 41–72 | **The loop:** call the model, check `stop_reason`, run the tool, repeat |

The line where the tool actually gets called is **line 64**:

```python
result = look_up_order(**block.input)
```

The model only *asks* for the tool. Your code runs it.

## Run it

From the repository root (see the main README for installing and setting your API key):

```bash
python lessons/lesson-03-build-your-first-agent/minidesk_v0.py
```

One run makes **two model calls** and **one real function call**:

1. **Call 1** returns `stop_reason: "tool_use"`, asking for `look_up_order` with order ID `A1001`.
2. **Your code** runs the real lookup: Wireless Mouse, delivered.
3. **Call 2** returns `stop_reason: "end_turn"` with a plain-English answer built from that result.

Example output (the wording will vary from run to run):

```
I found your order A1001. Here are the details:

Item: Wireless Mouse
Status: Delivered
Total: $24.99

Let me know if you'd like anything else checked or have questions about this order.
```

## Try this

- Change the ticket at the bottom of the file to order `A1002`, or to an ID that doesn't exist.
- Rename the function but not the schema's `"name"`, and see what breaks. They must match.
- Set `MAX_STEPS = 1` and see the circuit breaker stop the loop before the final answer.
