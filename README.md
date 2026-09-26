# AI Agents from Scratch

Code for the **AI Agents from Scratch** course on the YouTube channel **code with visualization**:
24 lessons that build a real AI agent in plain Python, with no frameworks. Every idea in the videos is animated step by step.

The running example is **MiniDesk**, a customer-support agent. It starts tiny and gains new capabilities
(memory, more tools, guardrails, evaluation) only once the lesson that makes them safe has been covered.

## Lessons

| # | Lesson | Code |
|---|--------|------|
| 1 | What Is an Agent, Really? | concepts only |
| 2 | Underneath the Agent | concepts only |
| 3 | Build Your First Agent | [`lessons/lesson-03-build-your-first-agent`](lessons/lesson-03-build-your-first-agent) |
| 4 | The Agent Loop, Live | coming soon |

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
    └── lesson-03-build-your-first-agent/
        ├── README.md         ← what this lesson builds, how to run it, expected output
        └── minidesk_v0.py    ← the code from the video
```
