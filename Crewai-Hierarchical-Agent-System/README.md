# CrewAI Command Center — Hierarchical Multi-Agent Business Analyzer

A production-architecture AI system where a Manager Agent autonomously delegates market research, strategy, and report writing to three specialized worker agents. Built as Day 3 of a 15-day CrewAI learning program.

---
Live Link: https://crewai-hierarchical-agent.streamlit.app/
## What This Actually Does

You describe a business idea. A Project Manager agent breaks the work down, assigns it to the right specialists, monitors their output, and consolidates a final business analysis report — without you specifying who does what.

This is not a chatbot wrapper. The manager makes autonomous delegation decisions at runtime. You cannot predict the exact subtask breakdown before running it — that is the point.

**Supported providers:**
- Gemini 2.5 Flash / 2.0 Flash (recommended — free tier works)
- Groq LLaMA 3.3 70B / Mixtral 8x7B (fallback — TPM limits apply on free tier)

---

## Architecture

```
User Input (business idea)
         │
         ▼
┌──────────────────────────────┐
│  Project Manager             │
│  allow_delegation = True     │
│                              │
│  · Breaks down the goal      │
│  · Assigns to specialists    │
│  · Reviews outputs           │
│  · Approves final report     │
└──────────────────────────────┘
     │           │           │
     ▼           ▼           ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│Research │ │Strategy  │ │Report    │
│Speciali-│ │Consultan-│ │Writer    │
│st       │ │t         │ │          │
│         │ │          │ │          │
│· TAM    │ │· Pricing │ │· Synthesis│
│· Compet.│ │· GTM     │ │· Structure│
│· Gaps   │ │· Risks   │ │· Polish  │
└─────────┘ └──────────┘ └──────────┘
     │           │           │
     └─────────┬─────────────┘
               ▼
    Manager reviews + consolidates
               │
               ▼
      Final Business Report
```

**Process:** `Process.hierarchical` — one task, four agents. The manager decides delegation order and depth at runtime.

**Key distinction from Day 2 (Sequential):** In sequential process, you explicitly assign each task to each agent. In hierarchical, the manager decides. This is closer to how real automation pipelines work.

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Agent framework | CrewAI | Native hierarchical process support |
| Primary LLM | Gemini 2.5 Flash | Free tier with usable RPM for multi-agent runs |
| Fallback LLM | Groq LLaMA 3.3 70B | Fast inference, but TPM limits hit quickly with 4 agents |
| UI | Streamlit | Fast deployment, secrets management built-in |
| Deployment | Streamlit Cloud | GitHub-connected, zero infrastructure |

---

## Presets

Four business ideas with detailed, specific descriptions that give agents enough context to produce genuinely useful output:

**AI Real Estate Deal Analyzer** — ROI/cap rate calculations, deal benchmarking against 50K historical transactions, targeting active investors evaluating 10+ deals/month.

**AI Legal Contract Assistant** — Contract review for solo lawyers billing $200–$500/hr, clause-level risk flagging, redline suggestions, 3-hour → 20-minute workflow target.

**AI Freelancer Growth Platform** — Profile optimization and proposal generation for Bangladeshi freelancers on Upwork/Fiverr, targeting the 500K+ active freelancers plateaued at entry-level income.

**AI Customer Support Automation** — Tier-1/Tier-2 ticket resolution for e-commerce brands doing $1M–$20M revenue, per-ticket pricing model, 60% headcount reduction target.

The quality of agent output is directly proportional to the specificity of input. Generic descriptions produce generic reports. These presets are written to demonstrate that.

---

## What the Delegation Log Shows

The UI renders a live timestamped log during execution:

```
0.0s  SYS  Crew initialized · Process.hierarchical · gemini
0.4s  MGR  Manager analyzing business idea…
0.7s  MGR  Delegating market research → Research Specialist
1.0s  RES  Research Specialist starting market analysis…
1.3s  MGR  Delegating strategy → Business Strategy Consultant
1.6s  STR  Strategy Consultant building monetization plan…
1.9s  MGR  Delegating report → Report Writer
```

This is a UI representation of the delegation sequence. The actual agent reasoning happens asynchronously inside CrewAI's execution engine.

---

## Local Setup

```bash
git clone https://github.com/sihabsafin/agentic-ai-projects
cd crewai-day3-hierarchical

pip install crewai[google-genai] google-generativeai litellm streamlit

# For Gemini (recommended)
export GEMINI_API_KEY=your_key   # aistudio.google.com/apikey

# For Groq (fallback)
export GROQ_API_KEY=your_key     # console.groq.com/keys

streamlit run app.py
```

---

## Streamlit Cloud Deployment

1. Push to GitHub — `app.py` and `requirements.txt`
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Settings → Secrets:
```toml
GEMINI_API_KEY = "your_gemini_key"
GROQ_API_KEY = "your_groq_key"
```
4. Deploy

**Note on free tier limits:** Gemini 2.5 Flash allows 5 RPM on the free tier. A 4-agent hierarchical run typically completes within 2–3 requests. Leave 30–60 seconds between runs to avoid hitting the per-minute ceiling. Groq's free tier hits TPM limits faster with multi-agent workloads — use Gemini as primary.

---

## Project Structure

```
crewai-day3-hierarchical/
├── app.py                # UI + hierarchical CrewAI logic
├── requirements.txt      # crewai[google-genai], google-generativeai, litellm, streamlit
└── README.md
```

---

## Progression Across Days

| | Day 1 | Day 2 | Day 3 |
|---|---|---|---|
| Agents | 1 | 2 | 4 |
| Tasks | 1 | 2 | 1 (delegated internally) |
| Process | Default | Sequential | Hierarchical |
| Task assignment | You assign | You assign | Manager decides |
| Review layer | None | None | Manager reviews before final output |
| Architecture pattern | Single analyst | Pipeline | Orchestrated team |

Each day's pattern is a building block. Day 3's hierarchical process only makes sense if you've felt the limitations of Day 1's single agent and Day 2's rigid sequential flow.

---

## Known Limitations

- Free tier Gemini allows 5 RPM — consecutive rapid runs will hit this ceiling
- Gemini 2.0 Flash has 0 RPD on the free tier despite appearing in some model lists — use 2.5 Flash
- The delegation log is a UI animation that approximates timing — it does not stream real CrewAI internal events
- `Process.hierarchical` requires the manager LLM to be capable enough to make delegation decisions — weak or small models will produce poor task breakdowns

---

*Part of `agentic-ai-projects` — a 15-day progressive build of multi-agent AI systems using CrewAI, from single-agent patterns to full automation pipelines.*
