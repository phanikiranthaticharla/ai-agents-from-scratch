"""
Lesson 4 - The Agent Loop, Live: count the steps.

Runs the SAME agent from Lesson 3 (minidesk_v0.py, unchanged) on two almost identical tickets
and prints every trip around the loop: what stop_reason came back, which tool the model
asked for, and what the real lookup returned.

Nothing in minidesk_v0.py is modified. This script only *watches* it:
it wraps the API call and the lookup function so each step gets printed.

usage:
    python count_steps.py                        # the Lesson 4 pair: and_then, then and_if_then
    python count_steps.py --ticket and_if_then   # just one ticket
    python count_steps.py --ticket normal        # the Lesson 3 ticket, for comparison
    python count_steps.py --runs 3               # optional: repeat each ticket to see it's consistent

Every run is saved to trace_log.json (the next run overwrites it).
Note: each run makes real API calls (billed per use). The default run makes about 7 small calls.
"""
import argparse
import json

import minidesk_v0 as md          # the exact Lesson 3 agent, imported as is

TICKETS = {
    # the Lesson 3 ticket: one order, one lookup
    "normal":      "Hi, can you check on order A1001?",
    # the Lesson 4 pair: same sentence, same four orders. The second only adds three "if" clauses,
    # and each one needs the answer to the lookup before it.
    "and_then":    "Hi, can you check on order A1001, and then A1002, and then A1003, and then A1004?",
    "and_if_then": ("Hi, can you check on order A1001, and if it's delivered, then A1002, and if that's in transit, "
                    "then A1003, and if that's not found, then A1004?"),
}
DEFAULT = ["and_then", "and_if_then"]

# ---------------------------------------------------------------- watching (not changing) the agent
trace = []                                   # steps of the current run

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
md.look_up_order = _watched_lookup           # run_agent() looks this name up at call time

# ---------------------------------------------------------------- run
def run_once(ticket):
    trace.clear()
    answer = md.run_agent(ticket)
    hit_cap = answer.startswith("stopped: exceeded MAX_STEPS")
    return {"steps": len(trace), "hit_max_steps": hit_cap, "answer": answer, "trace": list(trace)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticket", choices=list(TICKETS), help="run just one ticket")
    ap.add_argument("--runs", type=int, default=1, help="runs per ticket (default 1)")
    args = ap.parse_args()

    names = [args.ticket] if args.ticket else DEFAULT
    log, summary = {}, {}
    for name in names:
        ticket = TICKETS[name]
        log[name] = {"ticket": ticket, "runs": []}
        for r in range(1, args.runs + 1):
            print(f"\n=== {name}" + (f"  (run {r}/{args.runs})" if args.runs > 1 else "") + " ===")
            print(f"ticket: {ticket}")
            res = run_once(ticket)
            print(f"  -> {res['steps']} steps" + ("  (MAX_STEPS circuit breaker fired)" if res["hit_max_steps"] else ""))
            print(f"  answer: {res['answer']}")
            log[name]["runs"].append(res)
        summary[name] = [x["steps"] for x in log[name]["runs"]]

    print("\n================ SUMMARY (steps = trips around the loop = model calls) ================")
    for name in names:
        caps = sum(x["hit_max_steps"] for x in log[name]["runs"])
        steps = summary[name][0] if len(summary[name]) == 1 else summary[name]
        label = "steps:" if len(summary[name]) == 1 else "steps per run:"
        print(f"{name:12s} {label} {steps}" + (f"   circuit breaker fired {caps}x" if caps else ""))

    with open("trace_log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)
    print("\nfull traces saved to trace_log.json")


if __name__ == "__main__":
    main()
