# Resilient Analyzer — Error Handling + Retry Engine + Cost Optimization

An AI startup investment analyzer built with production reliability at its core. Every execution passes through a four-layer defense stack: input validation, retry-wrapped crew execution, two-pass JSON extraction, and schema + business logic validation. Built as Day 9 of a 15-day CrewAI learning program.

This is the project where the system stops being fragile and starts being trustworthy.

---

## The Problem This Solves

Days 1–8 produced working systems. Day 9 asks a harder question: what happens when it *doesn't* work?

API quota hits mid-run. The LLM wraps JSON in markdown. The user submits two words. The agent loops. Network times out.

A system that handles the happy path only is a demo. A system that handles failure gracefully is a product. Every layer in this project exists to answer one of those failure modes.

---

## Four-Layer Defense Stack

```
User Input
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 1: Input Validation          │
│  · Minimum length check             │
│  · Empty / generic input guard      │
│  · Maximum length cap               │
│  → Fails fast before any API call   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 2: Retry Engine              │
│  · Configurable attempts (1–5)      │
│  · Configurable delay between tries │
│  · Per-attempt live logging         │
│  · Stops on first success           │
│  → Survives transient API failures  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 3: JSON Extraction           │
│  · Pass 1: strip markdown, parse    │
│  · Pass 2: fix trailing commas,     │
│    unquoted keys, structural issues │
│  · Auto-regenerate on failure       │
│  → Never crashes on bad LLM output  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 4: Validation Pipeline       │
│  · Field presence checks            │
│  · Score range enforcement (0–10)   │
│  · Business logic: risk>8 → no Invest│
│  · Type check on recommended_actions│
│  → Every output is verified data    │
└─────────────────────────────────────┘
    │
    ▼
Structured output + Cost report
```

Each layer is independent. Layer 3 failing does not break Layer 4's attempt. Layer 2 exhausting retries surfaces a clear error instead of a silent crash.

---

## Implementation

### Layer 1 — Input Validation

```python
def validate_input(text: str, min_len: int = 30) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "Input is empty"
    if len(text.strip()) < min_len:
        return False, f"Too short — minimum {min_len} chars, got {len(text.strip())}"
    if len(text.strip()) > 3000:
        return False, "Too long — maximum 3000 characters"
    if text.strip().lower() in ["test", "hello", "startup", "idea"]:
        return False, "Too generic — describe with market size, pricing, and context"
    return True, "valid"
```

Runs before any API call. Fails fast. Saves tokens and quota on garbage input.

### Layer 2 — Retry Engine

```python
def safe_kickoff(crew, retries, delay, log_lines, log_ph, ts_fn):
    for attempt in range(1, retries + 1):
        try:
            log_lines.append((ts_fn(), "SYS", ..., f"Attempt {attempt}/{retries}…"))
            result = crew.kickoff()
            log_lines.append((ts_fn(), "OK", ..., f"Attempt {attempt} succeeded ✓"))
            return result, attempt, True
        except Exception as e:
            log_lines.append((ts_fn(), "ERR", ..., f"Attempt {attempt} failed: {e}"))
            if attempt < retries:
                time.sleep(delay)
    return last_error, retries, False
```

Every attempt is logged live to the mission log. The retry card row shows each attempt's status (PASS / FAIL) in real time as the run progresses.

### Layer 3 — JSON Extraction

```python
def extract_json_safe(text: str) -> dict:
    try:
        # Pass 1: strip markdown fences, find outermost braces
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    try:
        # Pass 2: fix trailing commas and unquoted keys
        fixed = re.sub(r',\s*}', '}', match.group())
        fixed = re.sub(r',\s*]', ']', fixed)
        return json.loads(fixed)
    except Exception:
        pass
    return {"error": "JSON extraction failed after two passes", "raw_preview": text[:300]}
```

Never calls `json.loads()` directly on LLM output. If both passes fail and `Auto-Regenerate` is enabled, the crew rebuilds and retries once more before surfacing an error.

### Layer 4 — Validation Pipeline

```python
def validate_output(data: dict) -> list:
    results = []
    # Field presence
    for key in required_keys:
        results.append(("✓" if key in data else "✗", key, ...))
    # Score range 0–10
    for score_key in ["market_score", "financial_score", "risk_score"]:
        val = data[score_key]
        results.append(("✓" if 0 <= val <= 10 else "✗", ...))
    # Business logic: risk > 8 cannot be Invest
    if data["risk_score"] > 8 and data["final_decision"] == "Invest":
        results.append(("✗", "risk/decision", "CONFLICT", False))
    # recommended_actions type check
    ra = data["recommended_actions"]
    results.append(("✓" if isinstance(ra, list) and len(ra) >= 3 else "⚠", ...))
    return results
```

Every check renders as ✓ / ✗ / ⚠ in the live validation panel. Nothing is hidden.

---

## Cost Optimization — What's Actually Built

**Concise Backstory Mode** — toggling this on shortens the agent backstory from ~60 words to ~20. The cost panel shows exactly how many tokens were saved per run and what percentage that represents.

**Temperature control** — slider from 0.0 to 1.0. Lower temperature means more deterministic, consistent JSON output with fewer malformed responses — directly reducing retry frequency and wasted tokens. 0.1–0.3 is the right range for structured output tasks.

**verbose=False (Production Mode)** — disabling CrewAI's internal verbose logging eliminates the hidden token overhead from step-by-step reasoning logs being written to console during execution.

**Cost panel** — every run displays estimated token count, estimated cost in USD (Gemini 2.5 Flash pricing), tokens saved from concise mode, and temperature setting. Not real billing data — estimates based on token approximation — but directionally accurate and demonstrates the principle.

The expert rule from Day 9 materials: *more agents ≠ better system, smarter architecture = cheaper system*. This project uses one agent intentionally. It does not need more.

---

## Test Mode — Intentional Failure Simulation

Three scenarios available via toggle:

**Bad Input** — sets the idea to "AI" (2 characters), triggering Layer 1 validation before any API call. Shows the system protecting itself from garbage input.

**Force JSON Extraction Recovery** — adds a hidden instruction telling the LLM to append extra text after the JSON, triggering the two-pass extraction fallback. Shows Layer 3 working.

**Simulate High-Risk Conflict** — injects a deliberately high-risk startup (meme coin launchpad) designed to produce risk_score > 8. If the agent still returns "Invest", the validation layer flags the business logic conflict with ✗. Shows Layer 4 catching the inconsistency.

These are not just demonstrations — they are the Day 9 assignment requirements implemented as interactive test scenarios.

---

## Live Mission Log

Every event is timestamped and tagged in real time during execution:

```
 0.0s  SYS    Reliability engine started · retries=3 · delay=2s · temp=0.2
 0.3s  SYS    Running input validation…
 0.5s  OK     Input valid ✓ — 312 chars
 0.8s  SYS    Crew built · Venture Capital Partner · backstory=concise · verbose=False
 1.1s  SYS    Attempt 1/3 — executing crew…
11.4s  OK     Attempt 1 succeeded ✓
11.5s  JSON   Running two-pass JSON extraction…
11.6s  JSON   JSON extracted successfully ✓
11.7s  VAL    Validation: ALL PASSED ✓
11.8s  COST   Est. tokens: 680 · Est. cost: $0.00005 · Saved: ~52 tokens (concise mode)
11.9s  SYS    Complete · 12.1s · attempts: 1/3
```

The retry card row above the log shows each attempt visually as PASS / FAIL / SKIP with timestamps.

---

## UI — System Health Bar

Five live status indicators render on page load before any run:

| Indicator | Reads |
|---|---|
| Gemini API | ONLINE (key present) / NO KEY |
| Groq Fallback | STANDBY / NO KEY |
| Retry Engine | ARMED (always) |
| Validation | ACTIVE (always) |
| Cost Guard | ACTIVE (always) |

This makes the system's operational state visible at a glance, before the user clicks anything.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Agent Framework | CrewAI |
| Retry Logic | Custom `safe_kickoff()` |
| JSON Extraction | Two-pass `extract_json_safe()` |
| Validation | Custom `validate_output()` pipeline |
| Primary LLM | Gemini 2.5 Flash |
| Fallback LLM | Groq LLaMA 3.3 70B |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

---

## Local Setup

```bash
git clone https://github.com/sihabsafin/agent-forge
cd crewai-day9-resilient

pip install crewai[google-genai] google-generativeai litellm streamlit

export GEMINI_API_KEY=your_key
export GROQ_API_KEY=your_key

streamlit run app.py
```

---

## Streamlit Cloud Deployment

```toml
GEMINI_API_KEY = "your_gemini_key"
GROQ_API_KEY = "your_groq_key"
```

`requirements.txt` — same as Day 8:
```
crewai[google-genai]
google-generativeai
litellm
streamlit
requests
```

---

## Progression: Day 8 → Day 9

| | Day 8 | Day 9 |
|---|---|---|
| Input validation | None | 4-rule validation gate |
| Execution | Single attempt | Retry engine (1–5 configurable) |
| JSON extraction | Two-pass | Two-pass + auto-regenerate fallback |
| Validation | Schema + logic | Schema + logic + live tagged log |
| Cost visibility | None | Token estimate + savings panel |
| Failure testing | None | 3 intentional failure scenarios |
| System health | None | Live 5-indicator health bar |
| Production readiness | Structured output | Structured output + resilient execution |

Day 8 proved the output can be structured. Day 9 proves the system can be trusted.

---

## Known Limitations

- Token and cost estimates are approximations, not real billing data — useful for understanding cost behavior directionally, not for invoicing
- Auto-regenerate adds a second API call — on Gemini free tier (5 RPM), leave 60s between runs if auto-regenerate triggered
- Test Mode's "Force JSON Recovery" scenario depends on the LLM following the injected instruction — not guaranteed on all models
- `safe_kickoff()` retries the entire crew on any exception, including quota errors — in a real production system, quota errors should be handled separately with exponential backoff

---

*Part of `agent-forge` — a 15-day progressive build of multi-agent AI systems using CrewAI.*
