"""
Lesson 5 - Prompting as Engineering: try the same agent with different system prompts.

Runs the SAME agent from Lesson 3 (minidesk_v0.py, unchanged). The only thing this script changes
is SYSTEM_PROMPT, swapped in at runtime, so every difference you see comes from the prompt.

For each experiment it runs one ticket with two prompts:
    vague  - a prompt with the key instruction missing (or a bad one added)
    clear  - the same prompt with one clear line that fixes it

and prints every trip (like count_steps.py in Lesson 4), the final answer, and a few automatic
"hints" to look for. The hints are simple text checks: always read the answer yourself.

usage:
    python try_prompts.py                          # every experiment, both prompts, one run each
    python try_prompts.py --exp no_eta             # one experiment
    python try_prompts.py --exp conflict --runs 3  # repeat, to see whether the behaviour is consistent
    python try_prompts.py --variant clear          # only the vague or only the clear prompt

Every run is saved to prompt_log.json (the next run overwrites it).
Note: each run makes real API calls (billed per use). All six experiments, both prompts, is about 25-30 small calls.
"""
import argparse
import json
import re

import minidesk_v0 as md          # the exact Lesson 3 agent, imported as is

BASE = md.SYSTEM_PROMPT           # the Lesson 3 prompt, exactly as it is in minidesk_v0.py
PLAIN = "Reply in plain text for a terminal: no Markdown, no asterisks, no bullet symbols."
ROLE = "You are a support agent for an online store. You can look up orders by ID. "
NO_ACTIONS = "You cannot issue refunds, cancellations, or any other action yet. "

AND_IF_THEN = ("Hi, can you check on order A1001, and if it's delivered, then A1002, and if that's in transit, "
               "then A1003, and if that's not found, then A1004?")

EXPERIMENTS = {
    # 1. the real Lesson 3 bug: without a format line, the answer is full of Markdown
    "markdown": dict(
        ticket="Hi, can you check on order A1001?",
        vague=ROLE + NO_ACTIONS,
        clear=BASE,
        look_for="Markdown in a terminal (**, # headings, - bullets) without the plain-text line",
    ),
    # 2. the data has a status but no delivery date: will the model invent one?
    "no_eta": dict(
        ticket="Hi, when will my order A1002 arrive?",
        vague=ROLE + NO_ACTIONS + PLAIN,
        clear=ROLE + NO_ACTIONS + PLAIN + " Only state facts returned by your tools. If a detail, such as a "
              "delivery date, isn't in the tool result, say you don't have it. Never estimate or invent it.",
        look_for="an invented delivery date or time frame",
    ),
    # 3. remove the 'you cannot issue refunds' line: will it claim to have done something it can't?
    "refund": dict(
        ticket="Hi, please refund my order A1001, the mouse stopped working.",
        vague=ROLE + PLAIN,
        clear=BASE + " If a customer asks for something you can't do, say so clearly and never suggest "
              "that it has been done.",
        look_for="claiming a refund was processed, issued or started",
    ),
    # 4. no order ID given: will it guess one?
    "missing_id": dict(
        ticket="Hi, where's my keyboard? I ordered it last week.",
        vague=ROLE + NO_ACTIONS + PLAIN,
        clear=BASE + " If the customer hasn't given an order ID, ask for it. Never guess or invent an order ID.",
        look_for="a lookup with an order ID the customer never gave",
    ),
    # 5. Lesson 4's 5-step ticket: can one line of prompt change the number of trips?
    "batch": dict(
        ticket=AND_IF_THEN,
        vague=BASE,
        clear=BASE + " When a customer mentions several orders, look them all up at once in a single step, "
              "then apply the customer's conditions to the results.",
        look_for="the number of steps (Lesson 4: 5 steps)",
    ),
    # 6. two instructions that contradict each other
    "conflict": dict(
        ticket="Hi, can you check on order A1002?",
        vague=BASE + " Always keep your answer to one short sentence. Always explain every detail of the order in full.",
        clear=BASE + " Keep answers short: one or two sentences with the key facts.",
        look_for="the answer length jumping around between runs (try --runs 3)",
    ),
}

# ---------------------------------------------------------------- watching (not changing) the agent
trace = []

_real_create = md.client.messages.create
def _watched_create(**kwargs):
    response = _real_create(**kwargs)
    asks = [f"{b.name}({', '.join(f'{k}={v!r}' for k, v in b.input.items())})"
            for b in response.content if b.type == "tool_use"]
    step = {"trip": len(trace) + 1, "stop_reason": response.stop_reason, "asks": asks, "results": []}
    trace.append(step)
    print(f"  trip {step['trip']}: stop_reason = {response.stop_reason}")
    for a in asks:
        print(f"          model asks for: {a}")
    return response
md.client.messages.create = _watched_create

_real_lookup = md.look_up_order
def _watched_lookup(order_id):
    result = _real_lookup(order_id)
    print(f"          your code ran:  look_up_order({order_id!r}) -> {result}")
    if trace:
        trace[-1]["results"].append({"order_id": order_id, "result": result})
    return result
md.look_up_order = _watched_lookup

# ---------------------------------------------------------------- simple hints (read the answer yourself!)
DATE = re.compile(r"\b(mon|tue|wed|thu|fri|sat|sun)[a-z]*day\b|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.? \d"
                  r"|\b\d+\s*(-|to)?\s*\d*\s*(business\s+)?(days?|weeks?)\b|\btomorrow\b|\bby the end of\b", re.I)
REFUND_DONE = re.compile(r"(refund|return)[^.]{0,40}\b(has been|have been|is being|was)\b[^.]{0,20}\b(processed|issued|initiated|"
                         r"started|approved|submitted)|\bI(?:'ve| have)\s+(processed|issued|initiated|started|submitted)"
                         r"|\bI(?:'ll| will| can)\s+(?:go ahead and\s+|help\s+)?(?:get\s+[^.]{0,30}\s+)?(process|issue|start|initiate|"
                         r"submit|proceed with|move forward with|flag)"
                         r"|\bonce (?:I have|you confirm)[^.]{0,40}\b(process|proceed)", re.I)
MARKDOWN = re.compile(r"\*\*|^\s*#{1,6}\s|^\s*[-*•]\s", re.M)


def hints(name, run):
    ans, h = run["answer"], []
    ids_in_ticket = set(re.findall(r"A\d{4}", EXPERIMENTS[name]["ticket"]))
    asked = [r["order_id"] for s in run["trace"] for r in s["results"]]
    if MARKDOWN.search(ans):
        h.append("Markdown found in the answer")
    if DATE.search(ans):
        h.append(f"mentions a date or time frame: {DATE.search(ans).group(0)!r}")
    if REFUND_DONE.search(ans):
        h.append(f"promises or claims an action it can't do: {REFUND_DONE.search(ans).group(0)!r}")
    guessed = [o for o in asked if o not in ids_in_ticket]
    if guessed:
        h.append(f"looked up order IDs the customer never gave: {guessed}")
    h.append(f"{run['steps']} steps, {len(asked)} lookups, {len(ans.split())} words")
    return h


def run_once(prompt, ticket):
    md.SYSTEM_PROMPT = prompt            # run_agent() reads this name on every call
    trace.clear()
    answer = md.run_agent(ticket)
    return {"steps": len(trace), "hit_max_steps": answer.startswith("stopped: exceeded MAX_STEPS"),
            "answer": answer, "trace": list(trace)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", choices=list(EXPERIMENTS), help="run just one experiment")
    ap.add_argument("--variant", choices=["vague", "clear", "both"], default="both")
    ap.add_argument("--runs", type=int, default=1, help="runs per prompt (default 1)")
    args = ap.parse_args()

    names = [args.exp] if args.exp else list(EXPERIMENTS)
    variants = ["vague", "clear"] if args.variant == "both" else [args.variant]
    log = {}
    for name in names:
        e = EXPERIMENTS[name]
        log[name] = {"ticket": e["ticket"], "look_for": e["look_for"]}
        for v in variants:
            log[name][v] = {"system_prompt": e[v], "runs": []}
            for r in range(1, args.runs + 1):
                print(f"\n=== {name} / {v} prompt" + (f"  (run {r}/{args.runs})" if args.runs > 1 else "") + " ===")
                print(f"ticket: {e['ticket']}")
                res = run_once(e[v], e["ticket"])
                res["hints"] = hints(name, res)
                print(f"  answer: {res['answer']}")
                for h in res["hints"]:
                    print(f"  hint: {h}")
                log[name][v]["runs"].append(res)
    md.SYSTEM_PROMPT = BASE

    print("\n================ SUMMARY (look for: the difference between the vague and the clear prompt) ================")
    for name in names:
        print(f"{name:11s} look for: {EXPERIMENTS[name]['look_for']}")
        for v in variants:
            for r in log[name][v]["runs"]:
                print(f"   {v:5s} -> " + " | ".join(r["hints"]))

    with open("prompt_log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)
    print("\nfull traces saved to prompt_log.json")


if __name__ == "__main__":
    main()
