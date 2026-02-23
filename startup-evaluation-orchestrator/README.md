# Startup Evaluation Orchestrator

> You can't improve what you can't measure. You can't debug what you can't trace.

A production-grade observability layer for multi-agent AI systems — built on top of the Day 7 due diligence crew. Adds structured logging, live monitoring metrics, execution timelines, failure tracking, and decision explainability to a four-agent CrewAI pipeline.

This is Day 11 of [`agent-forge`](https://github.com/sihabsafin/agent-forge), a 15-day progressive build series. Every previous day added capabilities. Day 11 adds **visibility** — the thing that separates a demo from something you'd actually run in production.

Live Link: https://startup-evaluation-orchestrator.streamlit.app/
---

![Python](https://img.shields.io/badge/Python-3.10%2B-4ade80?style=flat-square&logo=python&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Latest-22d3ee?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-fbbf24?style=flat-square&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-Primary-4ade80?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-60a5fa?style=flat-square)

---

## The Problem This Solves

Imagine you deployed the Day 7 due diligence system for a client. It runs 50 analyses per week. One day, a founder calls and asks: *"Why did your system recommend PASS on my startup?"*

Without observability, your answer is: *"I don't know — let me run it again and see."*

That is not a production system. That is a demo.

With observability, your answer is: *"At 14:23:07, the Risk Analyst assigned a 3/10 risk score due to regulatory uncertainty. The Investment Advisor weighted that heavily given the Pre-Seed stage. Confidence level was Medium. Decision reasoning: insufficient regulatory validation before capital deployment."*

That is the difference this project makes — and it is the difference between a system clients trust and one they don't.

---

## What Gets Logged and Why

Every meaningful event in the execution pipeline is captured:

```
14:23:01.441  INFO   === RUN #3 STARTED ===
14:23:01.442  INFO   Startup: LexAI | Stage: Pre-Seed | Model: gemini-2.5-flash
14:23:01.443  DEBUG  Investor: Venture Capital | Geography: Global | Depth: Standard
14:23:01.443  DEBUG  Input length: 312 chars
14:23:01.891  DEBUG  Initializing LLM...
14:23:02.104  INFO   LLM ready: gemini/gemini-2.5-flash
14:23:02.105  INFO   4 agents ready: Market · Financial · Risk · Investment Advisor
14:23:02.106  DEBUG  4 tasks configured: Market → Financial → Risk → Investment
14:23:02.107  INFO   Crew execution started...
14:23:58.220  INFO   Crew complete · exec_time=56.11s · total_time=57.03s
14:23:58.221  DEBUG  Market output: 1842 chars
14:23:58.221  DEBUG  Financial output: 1654 chars
14:23:58.222  DEBUG  Risk output: 2103 chars
14:23:58.223  INFO   Extracting JSON verdict...
14:23:58.224  INFO   JSON parsed OK · decision=PASS · confidence=Medium
14:23:58.225  INFO   Output validation passed — all required fields present
14:23:58.226  INFO   === RUN #3 COMPLETE · decision=PASS · time=57.03s ===
```

Every log line has a timestamp to millisecond precision, a level (INFO/DEBUG/WARNING/ERROR), and a structured message. This is not `print()` debugging. It is how production systems are built.

---

## Four Observability Pillars

### 1. Structured Logging

The logging system uses Python's built-in `logging` module with a custom `SessionLogHandler` that writes into Streamlit's session state instead of a file — because Streamlit Cloud doesn't support persistent file I/O across requests.

```python
class SessionLogHandler(logging.Handler):
    def emit(self, record):
        st.session_state["run_log"].append({
            "ts":    datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "level": record.levelname,
            "msg":   self.format(record),
        })

logger = logging.getLogger("agentforge.day11")
logger.setLevel(logging.DEBUG)
logger.addHandler(SessionLogHandler())
```

Why this matters: the logger is attached once per session using a handler guard (`if not logger.handlers`), which prevents duplicate log entries across Streamlit reruns — a common gotcha that breaks logging in Streamlit apps.

### 2. Live Monitoring Metrics

Four counters persist across every run within a session and update immediately after each execution:

| Metric | What It Tracks |
|---|---|
| **Total Runs** | Every analysis attempted, successful or not |
| **Failed Runs** | Validation failures + agent execution errors |
| **Avg Exec Time** | Rolling average of `total_time` across all runs |
| **Log Events** | Total number of structured log entries this session |

The failure rate is derived — `(failed / total) × 100` — not stored separately, which keeps the data model clean.

### 3. Execution Timeline

After each run, a horizontal bar chart renders agent-level timing proportionally across the total execution window:

```
LLM Init          ████                              0.2s
Agent Setup       ████                              0.1s
Task Pipeline     ██                                0.1s
Market Analysis   ████████████████                 14.2s
Financial Analysis████████████████                 14.1s
Risk Assessment   ████████████████                 14.0s
Investment Verdict████████████████                 13.8s
```

This makes performance characteristics visible. If Market Analysis consistently takes 3× longer than the others, you know where to optimize — tighter task descriptions, fewer `max_iter`, or a faster model.

### 4. Decision Explainability

The Investment Advisor is instructed to include a `decision_reasoning` field in its JSON output — a 1-2 sentence human-readable explanation of *why* it made the decision it made:

```json
{
  "startup_name": "LexAI",
  "market_score": 6,
  "financial_score": 5,
  "risk_score": 3,
  "overall_score": 5,
  "confidence_level": "Medium",
  "final_decision": "PASS",
  "decision_reasoning": "Despite adequate market size, the combination of zero traction, no domain expertise in the founding team, and direct competition from Harvey AI and Ironclad with $50M+ in funding creates an unfavorable risk-adjusted return profile at Pre-Seed."
}
```

This field is rendered prominently in the UI with a distinct left-bordered panel. When a client or stakeholder challenges a decision, `decision_reasoning` is the answer — not the model weights, not the prompt text. A plain English sentence that a non-technical person can read and respond to.

---

## Failure Modes and How Each Is Handled

The system handles three categories of failure, each logged and counted distinctly:

**Validation Failure** — caught before agents deploy. If the startup description is empty, the system logs a WARNING, increments the failure counter, and records the run in history as ERROR. The crew is never instantiated, which saves token cost and avoids noisy error output from CrewAI.

**LLM Initialization Failure** — caught after validation but before task execution. A bad API key, network timeout, or unavailable model hits here. Logged as ERROR with the full exception message.

**Agent Execution Failure** — caught during `crew.kickoff()`. Any exception from CrewAI, the LLM provider, or tool execution lands here. The failure counter increments, the elapsed time at point of failure is logged, and the run is recorded in history as ERROR so the failure rate metric stays accurate.

The intentional failure test built into the presets — "INTENTIONAL FAILURE TEST" — triggers the first category. Select it, click Deploy, and watch the failure counter increment and the ERROR event appear in the trace log.

---

## JSON Output Schema

Every successful run produces a structured JSON verdict. The schema adds two fields compared to Day 7:

```json
{
  "startup_name":       "string  — name of the analyzed startup",
  "market_score":       "integer — 0 to 10",
  "financial_score":    "integer — 0 to 10",
  "risk_score":         "integer — 0 to 10 (10 = safest)",
  "overall_score":      "integer — 0 to 10",
  "confidence_level":   "string  — High | Medium | Low",
  "final_decision":     "string  — INVEST | CONDITIONAL | WATCH | PASS",
  "decision_reasoning": "string  — 1-2 sentences explaining the decision"
}
```

**New in Day 11 vs Day 7:**
- `confidence_level` — the advisor's own assessment of how certain it is. A PASS with High confidence means the data clearly supports rejection. A PASS with Low confidence means the system flagged insufficient information to make a strong call.
- `decision_reasoning` — the explainability field. Non-negotiable for any client-facing deployment.

The parser uses a two-pass regex strategy. Pass 1 looks for a fenced ` ```json ``` ` block. Pass 2 falls back to matching any object containing `"final_decision"` — because LLMs occasionally drop the markdown fence under high token load. Both results are validated for required field presence before the UI renders.

---

## Run History

Every analysis — successful or failed — is recorded in the session's run history table:

```
#1   AI Medical Booking Platform    INVEST        67.3s
#2   AI Logistics Optimizer         CONDITIONAL   71.1s
#3   LexAI                          PASS          57.0s
#4   INTENTIONAL FAILURE TEST       ERROR          0.0s
#5   AI Farming Automation          WATCH         63.8s
```

This table persists across the entire browser session. The last 8 runs are shown in reverse chronological order. Decision chips are color-coded: green for INVEST, amber for CONDITIONAL/WATCH, red for PASS/ERROR. Run time for failures is the elapsed time at point of failure — `0.0s` for validation failures means no agent cost was incurred.

---

## Startup Presets

Four substantive presets plus one intentional failure case:

| Preset | Purpose |
|---|---|
| AI Medical Booking Platform | Strong traction, clear revenue model — likely INVEST or CONDITIONAL |
| AI Logistics Optimizer | Named clients, ARR, fundraising — good for high-score validation |
| AI Legal Document Analyzer | No traction, weak team credentials — good for low-score/PASS test |
| AI Farming Automation | Academic team, no revenue, niche market — tests nuanced reasoning |
| **INTENTIONAL FAILURE TEST** | Empty description — validates failure counter and ERROR logging |

Run all five in sequence to complete the Day 11 assignment criteria in under 10 minutes.

---

## Configuration

All settings under the **Observability Settings** expander affect agent behavior — not just labels:

**Log Level** — INFO captures all meaningful events. DEBUG adds input metadata, output character counts, and step-level timing. WARNING shows only anomalies and failures.

**Analysis Depth** — Brief, Standard, or Detailed changes the instruction length passed to each agent's task description, which directly affects output quality and execution time.

**Investor Lens** — Changes each agent's backstory and scoring emphasis. Venture Capital weights scalability and 10x potential; Impact Investor adds social impact metrics.

**Geography** — Adjusts market context. Selecting Southeast Asia tells the Market Analyst to reason about SEA market dynamics specifically, rather than defaulting to US/EU assumptions.

**Panel toggles** — Trace log, execution timeline, and JSON verdict can each be hidden independently — useful for presentations where you want to show only the final output without the infrastructure layer.

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| Agent Framework | [CrewAI](https://crewai.com) | Sequential multi-agent pipeline |
| Logging | Python `logging` + custom handler | Structured in-memory log capture |
| Monitoring | `st.session_state` counters | Persistent metrics across reruns |
| Primary LLM | Gemini 2.5 Flash | Main reasoning engine |
| Fallback LLM | Groq LLaMA 3.3 70B / Mixtral 8x7B | Rate limit fallback |
| LLM Router | LiteLLM | Provider-agnostic model switching |
| UI | Streamlit | Dashboard rendering |
| Deployment | Streamlit Cloud | Zero-config hosting |

---

## Local Setup

**1. Clone**
```bash
git clone https://github.com/sihabsafin/agent-forge
cd agent-forge/crewai-day11-observability
```

**2. Install**
```bash
pip install crewai[google-genai] google-generativeai litellm streamlit
```

**3. Environment**
```bash
export GEMINI_API_KEY="your_key"   # aistudio.google.com/apikey
export GROQ_API_KEY="your_key"     # console.groq.com/keys (optional)
```

**4. Run**
```bash
streamlit run app.py
```

---

## Streamlit Cloud Deployment

Place `requirements.txt` in the **repo root** (not inside the project subfolder — see the [Day 5 deployment note](../crewai-day5-real-apis/README.md) for why this matters):

```
crewai[google-genai]
google-generativeai
litellm
streamlit
```

Add secrets:
```toml
# Settings → Secrets
GEMINI_API_KEY = "your_gemini_key"
GROQ_API_KEY   = "your_groq_key"
```

No new dependencies compared to Day 7. The entire observability layer — logging, monitoring, tracing — is built from Python stdlib (`logging`, `time`, `datetime`) and Streamlit session state. Zero additional packages required.

---

## Day 11 Assignment — Completed

| Requirement | How |
|---|---|
| Run 5 startup ideas | 4 presets + custom input; run history records all |
| Check log file output | Full session trace log renders after every run; shows last 30 events live |
| Verify execution time logging | `exec_time` and `total_time` logged per run; timeline shows agent breakdown |
| Force 1 intentional failure | Select "INTENTIONAL FAILURE TEST" — failure counter increments, ERROR logged |
| Confirm failure counter increases | Metrics dashboard updates immediately; failure appears in run history as ERROR |

---

## The Broader Point

Every serious AI product eventually needs what this project implements. Not because it's technically complex — the logging here is straightforward Python — but because without it, you are flying blind.

When something breaks in production (and it will), you need to know which agent failed, what input it received, how long each step took, and what the system decided before the failure. When a client disputes a decision, you need to show them the reasoning chain, not re-run the analysis and hope you get the same answer.

Observability is not a feature. It is the foundation that makes every other feature trustworthy.

---

## Series Progression — agent-forge

| Day | Project | Core Concept |
|---|---|---|
| 1 | Single-agent writer | Agent + task basics |
| 2 | Research pipeline | Sequential multi-agent |
| 3 | Hierarchical system | Manager delegation |
| 4 | Market intelligence tool | Mock tool integration |
| 5 | Weather + Crypto dashboard | Real external APIs |
| 6 | Business memory system | ChromaDB vector memory |
| 7 | Startup due diligence | Multi-agent + JSON output |
| 8–10 | *(intermediate builds)* | — |
| **11** | **Observability System** | **Logging · Monitoring · Tracing** |
| 12–15 | Coming soon | — |

---

## License

MIT — use it, extend it, sell it. Attribution appreciated.

---

## Author

**Sihab Safin** — building [`agent-forge`](https://github.com/sihabsafin/agent-forge), a 15-day series of production-grade CrewAI systems.

- GitHub: [@sihabsafin](https://github.com/sihabsafin)
- Live demo: [aibusinessintelligence.streamlit.app](https://aibusinessintelligence.streamlit.app)

---

*If this helped you think differently about AI system design, a ⭐ on the repo costs nothing and helps others find it.*
