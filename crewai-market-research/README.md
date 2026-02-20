# CrewAI Market Research Agent

A single-agent AI system that performs structured market research on any business idea. Built with CrewAI, Groq (LLaMA 3.3 70B), and deployed via Streamlit.

---

## What It Does

You describe a business idea. The agent — configured with a specific role, goal, and professional backstory — autonomously produces a structured market research report covering market size, target audience, competitors, opportunities, and a final recommendation.

No hardcoded outputs. The agent reasons through the task independently on every run.

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

## Architecture

```
User Input (business idea)
        │
        ▼
   CrewAI Agent
  ┌─────────────────────────────┐
  │  Role: Market Research      │
  │  Analyst                    │
  │  Goal: Structured analysis  │
  │  Backstory: Domain expert   │
  └─────────────────────────────┘
        │
        ▼
  Groq LLM (LLaMA 3.3 70B)
        │
        ▼
  Structured Report Output
```

This is a **single-agent, single-task** system — the foundation pattern before moving to multi-agent crews.

---

## Key Concepts Demonstrated

- Agent design: role, goal, backstory, and how each shapes LLM behavior
- Task design: `description` vs `expected_output` — how output format is controlled
- LLM configuration: connecting CrewAI to Groq via the `LLM` class
- Streamlit deployment: secrets management, environment variables, live UI

---

## Presets Included

Three ready-to-run business ideas are built in:

- **AI Fitness App** — health tech market, competitor analysis, growth opportunities
- **AI YouTube Script Generator** — creator economy, SaaS pricing, GTM strategy
- **AI Real Estate Analyzer** — PropTech TAM/SAM/SOM, investment scoring

Custom input is also supported — describe any business idea and the agent adapts.

---

## Local Setup

```bash
git clone https://github.com/sihabsafin/agentic-ai-projects
cd crewai-market-research

pip install crewai litellm streamlit

# Set your Groq API key (free at console.groq.com/keys)
export GROQ_API_KEY=your_key_here

streamlit run app.py
```

---

## Streamlit Cloud Deployment

1. Push `app.py` and `requirements.txt` to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Add secret in app settings: `GROQ_API_KEY = "your_key"`
4. Deploy — live in ~2 minutes

---

## Project Structure

```
crewai-market-research/
├── app.py                  # Streamlit UI + CrewAI logic
├── requirements.txt        # crewai, litellm, streamlit
└── README.md
```

---

## What's Next (Day 2+)

This is Day 1 of a 15-day CrewAI learning program. Upcoming projects in this repo:

- **Day 2** — Multi-agent crew: Research Agent + Report Writer Agent (Sequential process)
- **Day 3** — Hierarchical process with a Manager Agent
- **Day 5** — Tool use: agents that search the web in real time
- **Day 10** — Full automation pipeline: input → research → analysis → PDF report

---

## Notes

- Groq's free tier is sufficient to run this — no paid API needed
- `OPENAI_API_KEY` is set to a dummy value in code; CrewAI requires the variable to exist even when not using OpenAI
- `verbose=False` is set to keep Streamlit logs clean; set to `True` locally to see agent reasoning steps

---

*Part of the `agentic-ai-projects` repository — a progressive series of multi-agent AI systems.*
