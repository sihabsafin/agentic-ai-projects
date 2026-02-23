# Modular Analyzer — Clean Architecture + Separation of Concerns

A fully modular AI startup investment analyzer where every layer of the system lives in its own file. The UI imports one function. The crew assembly imports from three modules. Tools have no knowledge of agents. Tasks have no knowledge of tools. Built as Day 10 of a 15-day CrewAI learning program.

This is the project where the system becomes maintainable.

---

## Project Structure

```
crewai-day10-modular/
│
├── app.py          ← UI only. Imports run_startup_analysis() from execution.py — nothing else.
├── execution.py    ← Pipeline orchestration. The only module app.py needs.
├── crew_setup.py   ← Crew assembly. Pulls from agents, tasks, tools. Returns Crew object.
├── agents.py       ← Agent definitions only. No task logic. Tools injected externally.
├── tasks.py        ← Task definitions + JSON schema. Single source of truth for schema.
├── tools.py        ← Custom tools. BaseTool subclasses. No agent logic.
├── utils.py        ← Shared utilities. No CrewAI imports. Pure Python.
└── requirements.txt
```

---

## Module Dependency Graph

```
app.py
  └── execution.py
        ├── crew_setup.py
        │     ├── agents.py       ← receives tools as parameters
        │     ├── tasks.py        ← receives agents as parameters
        │     └── tools.py        ← get_research_tools(), get_strategy_tools()
        └── utils.py              ← validate_input(), extract_json_safe(),
                                     validate_output(), safe_kickoff()
```

Each module has one responsibility. Changing how a tool works does not touch agents.py. Changing the JSON schema does not touch tools.py. Swapping an agent's model does not touch tasks.py.

This is separation of concerns in practice.

---

## What Each Module Does

### `tools.py`
Custom tool definitions — `MarketSizeTool`, `ROICalculatorTool`, `CompetitorIntelTool`. Each is a `BaseTool` subclass with a `name`, `description`, and `_run()` method. Tools export two registry functions — `get_research_tools()` and `get_strategy_tools()` — so crew_setup.py can assign the right tools to the right agents without knowing tool implementation details.

### `agents.py`
Agent definitions and nothing else. Each `create_*()` function takes an `llm` instance and optional `tools` list. No task logic, no schema, no execution. The backstory is intentionally concise — shorter backstory means fewer tokens per run.

```python
def create_market_analyst(llm, tools: list) -> Agent:
    return Agent(
        role="Market Research Specialist",
        goal="Use available tools to produce a data-backed market analysis...",
        backstory="Senior business intelligence analyst. Calls tools first, draws conclusions second.",
        llm=llm,
        tools=tools,
        verbose=False,
    )
```

### `tasks.py`
Task definitions and the JSON schema. The schema is defined once as `JSON_SCHEMA` — a module-level constant. Every task that needs structured output references this constant. Changing the schema here changes it everywhere. Tasks receive agent instances as parameters — they do not create agents.

### `crew_setup.py`
Single integration point. `create_startup_crew()` calls `get_research_tools()`, `create_all_agents()`, and the task creation functions — assembles them into a `Crew` object, and returns it without executing. Two modes: 5-agent specialist mode (sequential process, full specialist pipeline) and 1-agent direct mode (faster, lower cost, single Investment Advisor).

### `utils.py`
Pure Python utilities with zero CrewAI imports. This was a deliberate choice — `utils.py` can be unit tested without a CrewAI installation. Contains `validate_input()`, `extract_json_safe()` (two-pass JSON extraction), `validate_output()` (schema + business logic validation), `safe_kickoff()` (retry wrapper), and `estimate_cost()`.

### `execution.py`
The orchestration layer. `run_startup_analysis()` is the single function that app.py calls. It runs all five layers — input validation, crew setup, retry-wrapped execution, JSON extraction, and output validation — and returns a single structured result dict regardless of which layer succeeded or failed.

```python
def run_startup_analysis(startup_idea, model_id, api_key, ...) -> dict:
    # Layer 1: validate input
    # Layer 2: build LLM + crew
    # Layer 3: safe_kickoff with retries
    # Layer 4: extract JSON
    # Layer 5: validate output
    return {"success": bool, "data": dict, "validation": list, ...}
```

### `app.py`
UI only. Imports `run_startup_analysis` from `execution.py` — nothing else from the backend. Handles Streamlit layout, user inputs, live execution log, and rendering parsed results. The module dependency graph is displayed at the top of the UI so users can see the architecture before running anything.

---

## Why This Architecture Matters

### Changeability
If a client asks you to add a new tool — `LinkedInScraperTool` — you add one class to `tools.py` and register it in `get_research_tools()`. Nothing else changes.

If a client wants a different JSON schema — add a field — you change `JSON_SCHEMA` in `tasks.py`. One place. Done.

If you want to swap Gemini for GPT-4o — you change two lines in `execution.py`. The agents, tasks, and tools are unchanged.

### Reusability
`execution.run_startup_analysis()` can be called from a REST API, a CLI script, a Jupyter notebook, or a different Streamlit page. It is not coupled to any UI framework.

### Testability
Each module can be imported and tested independently. `utils.py` has no dependencies at all. `tools.py` can be tested with mock inputs. `agents.py` can be tested by injecting a mock LLM.

### GitHub readability
A recruiter or client opening the repo immediately understands the project structure from the file listing alone. No single 800-line notebook. Six focused files with clear names.

---

## 5-Agent vs 1-Agent Mode

**5-Agent Specialist Mode** — `use_specialists=True`

```
Market Research Specialist  (MarketSizeTool + CompetitorIntelTool)
    ↓ context
Financial Analyst           (ROICalculatorTool)
    ↓ context
Risk Analyst                (no tools — domain analysis)
    ↓ context
Investment Advisor          → final JSON synthesis
Manager                     → oversees (allow_delegation=False in sequential)
```

**1-Agent Direct Mode** — `use_specialists=False`

```
Investment Advisor → analyzes everything + returns JSON directly
```

Direct mode is ~3x faster and uses ~60% fewer tokens. Use it for rapid testing. Use specialist mode when the depth of analysis matters for the demo.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Agent Framework | CrewAI |
| Architecture | 6-module separation of concerns |
| Tools | `BaseTool` subclasses in `tools.py` |
| Schema | Enforced in `tasks.py` — single source of truth |
| Validation | `utils.py` — independent of CrewAI |
| Primary LLM | Gemini 2.5 Flash (free tier) |
| Fallback LLM | Groq LLaMA 3.3 70B |
| UI | Streamlit |

---

## Local Setup

```bash
git clone https://github.com/sihabsafin/agent-forge
cd crewai-day10-modular

pip install crewai[google-genai] google-generativeai litellm streamlit

export GEMINI_API_KEY=your_key
export GROQ_API_KEY=your_key

streamlit run app.py
```

All 7 files must be in the same directory — `app.py`, `execution.py`, `crew_setup.py`, `agents.py`, `tasks.py`, `tools.py`, `utils.py`.

---

## Deployment

```toml
# Streamlit Secrets
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

## Progression: Day 9 → Day 10

| | Day 9 | Day 10 |
|---|---|---|
| Files | 1 (app.py) | 7 (modular) |
| Architecture | Monolithic | Separated |
| Schema location | Inline in task string | `tasks.py` — single source |
| Tool location | Inline in app | `tools.py` — importable |
| Agent location | Inline in app | `agents.py` — reusable |
| Validation location | Inline in app | `utils.py` — independent |
| Entry point | `app.py` runs everything | `app.py` calls one function |
| Changeability | Touch everything to change one thing | Touch one module per concern |
| Testability | Must run full app | Each module testable independently |

Day 9 was resilient. Day 10 is maintainable.

---

## Known Limitations

- In Streamlit Cloud, all 7 files must be in the repo root or the same subdirectory — relative imports are used
- 5-agent specialist mode uses 4 sequential API calls and produces longer context — expect 30–60s runs on Gemini free tier
- The architecture diagram in the UI is HTML — cosmetic representation of the module graph, not auto-generated from live imports
- Cost estimates in the stats bar are approximations based on token count heuristics, not actual API billing

---

*Part of `agent-forge` — a 15-day progressive build of multi-agent AI systems using CrewAI.*
