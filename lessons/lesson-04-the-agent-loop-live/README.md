# Lesson 4 — The Agent Loop, Live

📺 **Watch the lesson:** [The Agent Loop, Live on YouTube](https://youtu.be/IT-3lbmWOeM)

New to the series? Start with [Lesson 1: What Is an Agent, Really?](https://youtu.be/xaMoPaBLgO4),
[Lesson 2: Underneath the Agent](https://youtu.be/lrfp7W4Qs3Q) and [Lesson 3: Build Your First Agent](https://youtu.be/JpsG3ZiXJak).

**Same code, two almost identical tickets. One finishes in 2 steps, the other takes 5.**
This lesson runs the Lesson 3 agent, unchanged, and prints every trip around the agent loop so you can see why.

## What's in this folder

| File | What it is |
|---|---|
| `minidesk_v0.py` | The agent from Lesson 3, **identical**, not one line changed |
| `count_steps.py` | Watches the agent: wraps the API call and `look_up_order` to print every trip. Changes nothing in the agent |
| `trace_and_then.json` | The real trace of the "and then" ticket shown in the video |
| `trace_and_if_then.json` | The real trace of the "and if … then" ticket shown in the video |

A **step** is one trip around the agent loop, which is **one API call**. At the end of every trip, the loop checks
`stop_reason`. `"tool_use"` means run the requested tools and go around again, and `"end_turn"` means done.

## The two tickets

| Ticket | Text | Trip 1 asks for | Steps |
|---|---|---|---|
| `and_then` | "Hi, can you check on order A1001, and then A1002, and then A1003, and then A1004?" | all four lookups at once | **2** |
| `and_if_then` | "Hi, can you check on order A1001, and **if it's delivered**, then A1002, and **if that's in transit**, then A1003, and **if that's not found**, then A1004?" | only A1001 | **5** |

The same four orders, the same four lookups, and the same final answer. The difference is the three "if"s: the model
can't check "if it's delivered" on an answer it hasn't seen yet, so **every if costs one more trip**.

## Run it

From the repository root (see the main README for installing and setting your API key):

```bash
cd lessons/lesson-04-the-agent-loop-live
python count_steps.py                        # both tickets: and_then, then and_if_then
python count_steps.py --ticket and_if_then   # just one
python count_steps.py --ticket normal        # the Lesson 3 ticket (2 steps), for comparison
python count_steps.py --runs 3               # repeat each ticket to see the count is consistent
```

One run of both tickets makes about **seven small model calls**. Every run is saved to `trace_log.json`
(the next run overwrites it).

Real output of the "and then" ticket (the answers will be worded differently each time; the steps won't):

```
=== and_then ===
ticket: Hi, can you check on order A1001, and then A1002, and then A1003, and then A1004?
  trip 1: stop_reason = tool_use
          model asks for: look_up_order(order_id='A1001')
          model asks for: look_up_order(order_id='A1002')
          model asks for: look_up_order(order_id='A1003')
          model asks for: look_up_order(order_id='A1004')
          your code ran:  look_up_order('A1001') -> {'item': 'Wireless Mouse', 'status': 'delivered', 'total': 24.99}
          your code ran:  look_up_order('A1002') -> {'item': 'Mechanical Keyboard', 'status': 'in transit', 'total': 89.0}
          your code ran:  look_up_order('A1003') -> {'error': 'no order found with id A1003'}
          your code ran:  look_up_order('A1004') -> {'error': 'no order found with id A1004'}
  trip 2: stop_reason = end_turn
  -> 2 steps
```

And the "and if … then" ticket, one lookup per trip:

```
=== and_if_then ===
  trip 1: stop_reason = tool_use
          model asks for: look_up_order(order_id='A1001')
          your code ran:  look_up_order('A1001') -> {'item': 'Wireless Mouse', 'status': 'delivered', 'total': 24.99}
  trip 2: stop_reason = tool_use
          model asks for: look_up_order(order_id='A1002')
          your code ran:  look_up_order('A1002') -> {'item': 'Mechanical Keyboard', 'status': 'in transit', 'total': 89.0}
  trip 3: stop_reason = tool_use
          model asks for: look_up_order(order_id='A1003')
          your code ran:  look_up_order('A1003') -> {'error': 'no order found with id A1003'}
  trip 4: stop_reason = tool_use
          model asks for: look_up_order(order_id='A1004')
          your code ran:  look_up_order('A1004') -> {'error': 'no order found with id A1004'}
  trip 5: stop_reason = end_turn
  -> 5 steps
```

## A note on "not found"

A1003 and A1004 don't exist in the stand-in database, and the agent says so instead of making something up.
But notice how guessable the IDs are. In a real store, `look_up_order` would also need to check that the order
**belongs to the person asking**. Hard-to-guess IDs slow an attacker down; an ownership check in your code stops them.
MiniDesk gets that check in the guardrails lessons later in the course.

## Try this

- Write your own ticket: add it to the `TICKETS` dictionary in `count_steps.py`, **guess the number of steps**, then run it.
- Add a couple more "if"s to `and_if_then`. With `MAX_STEPS = 6`, when does the circuit breaker fire, and why?
- Ask about two orders where the second depends on the first, and two where it doesn't. Can you predict the trips?

Next: [Lesson 5 — Prompting as Engineering](../../README.md#lessons) (coming soon).
