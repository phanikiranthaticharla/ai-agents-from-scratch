# Lesson 5 — Prompting as Engineering

📺 **Watch the lesson:** [Prompting as Engineering on YouTube](https://youtu.be/z3aIJCzRs0w)

New to the series? Start with [Lesson 1: What Is an Agent, Really?](https://youtu.be/xaMoPaBLgO4),
then [Lesson 2](https://youtu.be/lrfp7W4Qs3Q), [Lesson 3](https://youtu.be/JpsG3ZiXJak) and [Lesson 4](https://youtu.be/IT-3lbmWOeM).

**The agent promised a customer a refund. There is no refund tool. No code changed: one sentence was missing from the system prompt.**
This lesson runs the Lesson 3 agent, unchanged, with different system prompts, so every difference you see comes from the prompt.

## What's in this folder

| File | What it is |
|---|---|
| `minidesk_v0.py` | The agent from Lesson 3, **identical**, not one line changed |
| `try_prompts.py` | Runs one ticket with two system prompts and prints every trip, the answer, and a few hints. Swaps only `SYSTEM_PROMPT`, at runtime |
| `prompt_log_refund.json` | The real log of the refund experiment shown in the video (3 runs per prompt) |

The **system prompt** is the text you, the developer, write once. It goes out with every customer's ticket, on every
trip around the loop, in its own slot of the API call (`system=SYSTEM_PROMPT`, line 48). So every line in it is a
standing rule, and every missing line is a gap the model fills on its own.

## Run it

From the repository root (see the main README for installing and setting your API key):

```bash
cd lessons/lesson-05-prompting-as-engineering
python try_prompts.py --exp refund --runs 3     # the experiment from the video
python try_prompts.py --exp markdown            # one experiment, both prompts
python try_prompts.py                           # every experiment, both prompts, one run each
python try_prompts.py --exp refund --variant vague   # only one of the two prompts
```

All six experiments with both prompts is about 25–30 small model calls. Every run is saved to `prompt_log.json`
(the next run overwrites it, and it's ignored by git).

## The experiments

Each experiment runs one ticket with a **vague** prompt (the key line missing) and a **clear** prompt (the same prompt plus one line).

| Experiment | Ticket | The line that differs | What we saw |
|---|---|---|---|
| `markdown` | "Hi, can you check on order A1001?" | "Reply in plain text for a terminal: no Markdown, no asterisks, no bullet symbols." | Without it: `**Item:**` and `-` bullets printed raw in the terminal. With it: clean plain text |
| `refund` | "Hi, please refund my order A1001, the mouse stopped working." | "You cannot issue refunds…" plus "If a customer asks for something you can't do, say so clearly and never suggest that it has been done." | Without it: offered to start or process a refund **every run**. With it: said it can't, **every run** |
| `no_eta` | "Hi, when will my order A1002 arrive?" | "If a detail, such as a delivery date, isn't in the tool result, say you don't have it." | No difference: it already said it has no delivery date |
| `missing_id` | "Hi, where's my keyboard? I ordered it last week." | "If the customer hasn't given an order ID, ask for it." | No difference: it already asked for the order ID |
| `batch` | Lesson 4's "and if … then" ticket | "Look them all up at once in a single step…" | Still **5 steps**. A prompt can't remove a real dependency |
| `conflict` | "Hi, can you check on order A1002?" | Two rules that contradict each other | Nothing clear to show. Try it with `--runs 3` and judge for yourself |

### The refund experiment (from `prompt_log_refund.json`)

Without the line, run 3:

```
I'm sorry to hear the mouse stopped working. I can go ahead and process a refund for this order.
Before I do, could you confirm a couple of things: ...
```

With the line, run 2:

```
As noted, I'm unable to process a refund myself. Please reach out to our customer service team ...
```

There is no refund tool in `minidesk_v0.py` (`TOOLS` has only `look_up_order`), so the first answer is a promise
nothing will keep. The customer waits for a refund that never comes.

> **Read the answers, not just the hints.** The hints are simple text checks. In the saved log you can see the first
> version of the check didn't flag "I can go ahead and process a refund". Reading the real answers caught it, and the
> check in `try_prompts.py` has since been fixed. Proper evaluation comes later in the course.

## What a system prompt should say

1. **Who the agent is, and what it's for** (line 35)
2. **What it can do, what it can't, and what to say when a customer asks for something it can't do** (line 36, plus the refund line)
3. **What to do when information is missing: ask, don't guess** (add it when a real run shows you need it)
4. **How to use its tools** (the tool's `description`, lines 23–24)
5. **Where the answer will be shown**, so it picks the right format (line 37)

Vague lines like "be helpful and accurate" add nothing: the model is already trying to be both.

## Try this

- **Delete a line** from the prompt in an experiment, run it, and see what changes.
- Add a rule of your own. Does a real run show you need it, or was the model already right without it?
- Keep your prompt versions and test every change on the same tickets, like code.

Next: Lesson 6 — Tool Use & Function Calling (coming soon).
