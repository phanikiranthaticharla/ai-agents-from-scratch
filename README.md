# AI Agents from Scratch

Code for the **AI Agents from Scratch** course on the YouTube channel **code with visualization**:
24 lessons that build a real AI agent in plain Python, with no frameworks. Every idea in the videos is animated step by step.

The running example is **MiniDesk**, a customer-support agent. It starts tiny and gains new capabilities
(memory, more tools, guardrails, evaluation) only once the lesson that makes them safe has been covered.

## Lessons

| # | Lesson | Video | Code |
|---|--------|-------|------|
| 1 | What Is an Agent, Really? | [▶ watch](https://youtu.be/xaMoPaBLgO4) | concepts only |
| 2 | Underneath the Agent | [▶ watch](https://youtu.be/lrfp7W4Qs3Q) | concepts only |
| 3 | Build Your First Agent | [▶ watch](https://youtu.be/JpsG3ZiXJak) | [`lessons/lesson-03-build-your-first-agent`](lessons/lesson-03-build-your-first-agent) |
| 4 | The Agent Loop, Live | [▶ watch](https://youtu.be/IT-3lbmWOeM) | [`lessons/lesson-04-the-agent-loop-live`](lessons/lesson-04-the-agent-loop-live) |
| 5 | Prompting as Engineering | [▶ watch](https://youtu.be/z3aIJCzRs0w) | [`lessons/lesson-05-prompting-as-engineering`](lessons/lesson-05-prompting-as-engineering) |
| 6 | Tool Use & Function Calling | coming soon | |

Each lesson folder is a **complete, runnable snapshot** of MiniDesk at that point in the course.
Folders never change after their video is published, so the code always matches what you saw on screen.

## Quick start

```bash
git clone https://github.com/phanikiranthaticharla/ai-agents-from-scratch.git
cd ai-agents-from-scratch
pip install -r requirements.txt
```

Get an API key at [console.anthropic.com](https://console.anthropic.com) (API Keys), then set it as an
environment variable. Never paste the key into the code.

```bash
# Mac / Linux
export ANTHROPIC_API_KEY="your-key"

# Windows (PowerShell), for this terminal window only
$env:ANTHROPIC_API_KEY="your-key"
# ...or permanently (then open a new terminal)
setx ANTHROPIC_API_KEY "your-key"
```

Run a lesson:

```bash
python lessons/lesson-03-build-your-first-agent/minidesk_v0.py

cd lessons/lesson-04-the-agent-loop-live
python count_steps.py

cd ../lesson-05-prompting-as-engineering
python try_prompts.py --exp refund --runs 3
```

> API calls are billed per use. Each lesson's README says how many model calls one run makes.
> The model's replies are not word-for-word repeatable, so your output may be worded differently from the video.

## Repository layout

```
ai-agents-from-scratch/
├── README.md                 ← you are here
├── requirements.txt          ← shared dependencies
├── .gitignore
└── lessons/
    ├── lesson-03-build-your-first-agent/
    │   ├── README.md         ← what this lesson builds, how to run it, expected output
    │   └── minidesk_v0.py    ← the code from the video
    ├── lesson-04-the-agent-loop-live/
    │   ├── README.md
    │   ├── minidesk_v0.py    ← identical to Lesson 3
    │   ├── count_steps.py    ← watches the agent and prints every trip
    │   ├── trace_and_then.json
    │   └── trace_and_if_then.json
    └── lesson-05-prompting-as-engineering/
        ├── README.md
        ├── minidesk_v0.py    ← identical to Lesson 3
        ├── try_prompts.py    ← same agent, different system prompts, side by side
        └── prompt_log_refund.json
```
