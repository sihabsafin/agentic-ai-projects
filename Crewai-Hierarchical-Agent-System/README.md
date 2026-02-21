# CrewAI Command Center — Hierarchical Agent System

A four-agent AI system with a Manager Agent that delegates, reviews, and consolidates work from three specialist workers. Built with CrewAI's hierarchical process, Groq (LLaMA 3.3 70B), and Streamlit.

---
Live URL : 
## What It Does

You describe a business idea. A Manager Agent breaks the work down and delegates to three specialists — a Market Researcher, a Strategy Consultant, and a Report Writer. After workers complete their tasks, the manager reviews outputs, improves weak sections, and delivers a final consolidated business report.

This is how production AI automation systems are actually architected.

---

## How It Works

```
User Input
     │
     ▼
┌─────────────────────────┐
│  Project Manager        │  allow_delegation=True
│  · Breaks down goal     │  Owns the main task
│  · Assigns to workers   │  Reviews final output
│  · Approves report      │
└─────────────────────────┘
     │          │          │
     ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────────┐
│Research │ │Strategy │ │   Report    │
│Specialist│ │Consultant│ │   Writer    │
│· Market │ │· Pricing │ │· Synthesize │
│· Compete │ │· GTM     │ │· Structure  │
│· Opport.│ │· Risks   │ │· Polish     │
└─────────┘ └─────────┘ └─────────────┘
     │          │          │
     └──────────┴──────────┘
                │
                ▼
     Manager reviews + approves
                │
                ▼
      Final Business Report
```

**Process type:** `Process.hierarchical` — the manager owns a single task and autonomously decides how to delegate, sequence, and review worker outputs. No explicit task-to-agent assignment needed.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Agent Framework | CrewAI |
| LLM Provider | Groq (free tier) |
| Model | LLaMA 3.3 70B / LLaMA 3.1 8B / Mixtral 8x7B |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

---

## Key Concepts Demonstrated

**Hierarchical process** — one manager task, four agents. The manager decides who does what and when. Workers never receive tasks directly from you — only from the manager.

**`allow_delegation=True`** — this single flag is what enables a manager agent to assign work to others. Without it, the agent acts alone. With it, it becomes an orchestrator.

**Manager as reviewer** — the manager's instructions include reviewing worker outputs and improving weak sections before finalizing. This is real quality control baked into the architecture.

**Worker specialization** — each worker has a tight role, goal, and backstory. Narrow specialization consistently outperforms broad generalist agents.

---

## Day 1 → Day 2 → Day 3 Progression

| | Day 1 | Day 2 | Day 3 |
|---|---|---|---|
| Agents | 1 | 2 | 4 |
| Tasks | 1 | 2 | 1 (delegated) |
| Process | Default | Sequential | Hierarchical |
| Task assignment | Manual | Manual | Manager decides |
| Review step | None | None | Manager reviews |
| Architecture | Analyst | Researcher + Strategist | Manager + 3 Workers |

---

## Presets Included

- **AI Real Estate Deal Analyzer** — PropTech, investor tools, rental yield prediction
- **AI Legal Contract Assistant** — LegalTech, contract automation, solo law firms
- **AI Dropshipping Product Hunter** — ecommerce, Shopify, product research
- **AI Personal Finance Coach** — fintech, millennial targeting, spending analysis

---

## Local Setup

```bash
git clone https://github.com/sihabsafin/agentic-ai-projects
cd crewai-day3-hierarchical

pip install crewai litellm streamlit

export GROQ_API_KEY=your_key_here

streamlit run app.py
```

---

## Streamlit Cloud Deployment

1. Push `app.py` and `requirements.txt` to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Add secret: `GROQ_API_KEY = "your_key"`
4. Deploy — same `requirements.txt` as Day 1 and 2

---

## Project Structure

```
crewai-day3-hierarchical/
├── app.py               # Streamlit UI + hierarchical CrewAI logic
├── requirements.txt     # crewai, litellm, streamlit
└── README.md
```

---

*Part of the `agentic-ai-projects` repository — a progressive series of multi-agent AI systems built across a 15-day CrewAI learning program.*
