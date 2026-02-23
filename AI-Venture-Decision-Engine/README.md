# AI Venture Decision Engine — Structured AI Output + JSON Validation

An AI startup investment analyzer that enforces strict JSON schema on every output, runs a multi-layer validation pipeline, and renders structured scores, decisions, and actions directly from the parsed data. Built as Day 8 of a 15-day CrewAI learning program.

This is the project where the output stops being text and starts being data.

---

## What This Does

You describe a startup. An AI analyst agent evaluates it and returns a strict JSON object — market score, financial score, risk score, final decision, confidence level, and five recommended actions. The app extracts the JSON, validates the schema, checks business logic consistency, and renders every field as a live UI component.

Nothing in the UI is hardcoded. Every score card, decision banner, and action item is rendered from the parsed JSON returned by the agent.

---

## Why This Matters

The difference between a hobbyist AI project and a SaaS-ready system is structured output.

An agent that returns prose is useful once. An agent that returns validated JSON can be connected to a database, trigger a workflow, feed a frontend, power an API endpoint, or be compared against other outputs systematically. That's what this project demonstrates.

---

## Three Layers Implemented

### 1. Schema Enforcement
The agent task description includes the exact JSON schema and strict instructions — field names, data types, allowed values, and calculation rules. The agent is told to return only the JSON object with no text before or after it.

```json
{
  "market_score": 0-10,
  "market_summary": "string",
  "financial_score": 0-10,
  "financial_summary": "string",
  "risk_score": 0-10,
  "risk_summary": "string",
  "final_decision": "Invest / Consider / Reject",
  "confidence_level": "Low / Medium / High",
  "recommended_actions": ["string", "string", "string", "string", "string"],
  "total_score": float
}
```

### 2. Extraction Layer
LLMs occasionally wrap JSON in markdown fences or add explanatory text. The extraction function handles this:

```python
def extract_json(text: str) -> dict | None:
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            # Second pass: fix common LLM JSON issues
            fixed = re.sub(r',\s*}', '}', match.group())
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(fixed)
    return None
```

This is a production pattern. Never call `json.loads()` directly on LLM output.

### 3. Validation Layer
Every parsed output runs through a validation pipeline that checks:

- **Field presence** — all 6 required fields must exist
- **Score range** — `market_score`, `financial_score`, `risk_score` must be integers 0–10
- **Business logic** — if `risk_score > 8`, `final_decision` must not be "Invest" — a conflict is flagged
- **Type check** — `recommended_actions` must be a non-empty list

```python
def validate_output(data: dict) -> list:
    results = []
    # presence checks
    for key in required_keys:
        results.append(("✓" if key in data else "✗", key, ...))
    # range checks
    for score_key in ["market_score", "financial_score", "risk_score"]:
        val = data[score_key]
        results.append(("✓" if 0 <= val <= 10 else "✗", ...))
    # business logic: high risk → cannot be Invest
    if data["risk_score"] > 8 and data["final_decision"] == "Invest":
        results.append(("⚠", "risk+decision", "CONFLICT", False))
    return results
```

Each check renders as ✓ / ✗ / ⚠ in the validation panel. Every run, every output, every field — checked.

---

## Features

**Single Analysis Mode** — analyze one startup idea with configurable analyst persona, investment stage, and risk tolerance. Output renders as decision banner, score cards with progress bars, validation panel, recommended actions list, and colorized raw JSON.

**Comparison Mode** — runs all 4 preset startups sequentially through the same analyst with the same criteria. Renders a summary comparison table (market / financial / risk / total / decision / confidence) followed by individual full-panel analyses for each startup. One click shows four structured outputs side by side.

**Analyst Configuration** — four analyst personas (Venture Capital Partner, Angel Investor, Private Equity Analyst, Startup Accelerator), four investment stages (Pre-seed to Series B+), and three risk tolerance settings (Conservative / Balanced / Aggressive). The same startup analyzed by a conservative VC vs an aggressive accelerator will produce different scores.

**Colorized JSON Panel** — every run shows the raw extracted JSON with syntax highlighting — keys in blue, strings in green, numbers in amber, arrays in red. Demonstrates that the output is real structured data, not formatted prose.

---

## Presets

All four are written with enough specificity to produce meaningfully different outputs:

**AI Logistics Optimizer** — B2B SaaS for e-commerce shipping optimization, $2K–$8K/month pricing, $75B TAM at 14% CAGR, proprietary ML model as moat. Typically scores well — good opener for demos.

**AI Legal Document Analyzer** — contract intelligence for solo lawyers, $149/month flat, $12B LegalTech market. Interesting tension: strong market but liability risk for missed clauses creates a nuanced output.

**AI Recruitment Screening Tool** — HR candidate screening, $500/month per job posting, $28B TAM. High risk score expected due to EU/US AI hiring regulations — good test of the risk/decision conflict validator.

**AI Crypto Trading Bot** — retail algo trading, $99/month + performance fee, $2.3B TAM. Intentionally high-risk preset — regulatory uncertainty, user loss liability, and quant competition should push risk score above 8, triggering the validation warning if the agent incorrectly decides "Invest."

---

## Tech Stack

| Layer | Choice |
|---|---|
| Agent Framework | CrewAI |
| Output Control | Task description schema enforcement |
| JSON Extraction | `re` + `json` with two-pass fallback |
| Validation | Custom `validate_output()` pipeline |
| Primary LLM | Gemini 2.5 Flash (free tier) |
| Fallback LLM | Groq LLaMA 3.3 70B |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

---

## Local Setup

```bash
git clone https://github.com/sihabsafin/agent-forge
cd crewai-day8-structured-output

pip install crewai[google-genai] google-generativeai litellm streamlit requests

export GEMINI_API_KEY=your_key    # aistudio.google.com/apikey
export GROQ_API_KEY=your_key      # optional fallback

streamlit run app.py
```

---

## Streamlit Cloud Deployment

```toml
# Settings → Secrets
GEMINI_API_KEY = "your_gemini_key"
GROQ_API_KEY = "your_groq_key"
```

`requirements.txt`:
```
crewai[google-genai]
google-generativeai
litellm
streamlit
requests
```

---

## Progression: Day 1 → Day 8

| | Day 1 | Day 3 | Day 4 | Day 5 | Day 8 |
|---|---|---|---|---|---|
| Output type | Prose | Prose | Prose | Prose | Strict JSON |
| Schema | None | None | None | None | Enforced |
| Extraction | None | None | None | None | Two-pass parser |
| Validation | None | None | None | None | 8+ checks |
| UI binding | Text box | Text box | Text panels | Data cards | Schema-driven |
| DB ready | No | No | No | No | Yes |

Every previous day, the agent's output was text displayed in a panel. Day 8 is the first day the output is data that drives the UI. That's the shift.

---

## Known Limitations

- Schema enforcement relies on prompt instructions — very occasionally the LLM will return prose despite instructions, especially with smaller/weaker models. The extraction layer catches most cases; if it fails, the raw output is displayed.
- `total_score` is recalculated client-side as a fallback if the agent returns an incorrect calculation — the formula is `(market_score + financial_score + (10 - risk_score)) / 3`
- Comparison mode runs 4 sequential API calls — on Gemini's free tier (5 RPM), a 1.5s buffer is included between calls. Leave ~60 seconds between running single analysis and comparison mode.
- All investment analysis is AI-generated for learning demonstration purposes. Not financial advice.

---

## What Comes Next

Once output is structured and validated, the next logical step is connecting it to something — a database, an API, a notification system. That's where multi-agent automation pipelines begin.

---

*Part of `agent-forge` — a 15-day progressive build of multi-agent AI systems using CrewAI.*
