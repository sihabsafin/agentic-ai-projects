#AI Business Intelligence — Live Data Intelligence

AI agents that call real external APIs, parse live JSON responses, and generate structured analysis. No mock data. No hardcoded numbers. Every run fetches from the actual internet.

Built as Day 5 of a 15-day CrewAI learning program — the first day agents stopped writing from memory and started acting on the world.

Live Link: https://ai-business-intelligence.streamlit.app/
---

## What This Does

Three intelligence modes — each one powered by real API calls:

**Weather Intelligence** — Enter any city. The agent calls Open-Meteo's geocoding API to resolve coordinates, then the forecast API to fetch live temperature, humidity, wind speed, apparent temperature, and weather condition code. The agent interprets the raw JSON and writes a structured weather briefing.

**Crypto Market Intelligence** — Select up to 6 cryptocurrencies. The agent calls CoinGecko's public price API to fetch live USD price, 24h price change percentage, market cap, and trading volume for each asset. The agent analyzes the data and produces a market intelligence report.

**Combined Market Brief** — Two specialized agents run in sequence. The Weather Specialist handles Open-Meteo, the Crypto Specialist handles CoinGecko. Both outputs are visible in separate panels so you can see exactly which agent fetched which data.

Both APIs are completely free — no API key required.

---

## What's Actually Happening Under the Hood

```
User selects city / coins
        │
        ▼
App pre-fetches live data       ← real HTTP request before agents run
Shows live data cards           ← temperature, price, 24h change displayed
        │
        ▼
CrewAI agent runs
        │
        ├── calls WeatherTool._run(city)
        │       → GET geocoding-api.open-meteo.com
        │       → GET api.open-meteo.com/v1/forecast
        │       → parses JSON, returns structured string
        │
        └── calls CryptoPriceTool._run("bitcoin,ethereum,...")
                → GET api.coingecko.com/api/v3/simple/price
                → parses JSON, returns price + change + market cap
        │
        ▼
Agent receives tool output
Writes analysis grounded in real numbers
```

The app also pre-fetches the data before the agent runs and renders live data cards (temperature, crypto prices, 24h changes) so you can see the raw API response independently of what the agent says about it.

---

## The Core Day 5 Lesson

The reason tools exist is so that **logic and data fetching happen in Python, not in the LLM**.

The LLM should never be responsible for knowing Bitcoin's current price, or today's temperature in Dhaka. It cannot know these things reliably. The tool fetches the data — the LLM interprets it.

This separation is what makes the system trustworthy. Every number in the agent's output came from a live API call, not a language model's training data.

---

## Tools Built

### WeatherTool
```python
class WeatherTool(BaseTool):
    name = "Weather Data Tool"
    description = "Fetches real-time weather data for any city using 
                   the Open-Meteo API..."
    def _run(self, city: str) -> str:
        # 1. Call geocoding API to get lat/lon
        # 2. Call forecast API with coordinates
        # 3. Parse JSON response
        # 4. Return structured string with all weather fields
        # 5. Handle city not found + timeout + API errors
```

Returns: temperature, feels-like, humidity, wind speed, precipitation, condition code mapped to human-readable label.

### CryptoPriceTool
```python
class CryptoPriceTool(BaseTool):
    name = "Crypto Price Tool"
    description = "Fetches real-time cryptocurrency prices from 
                   CoinGecko public API..."
    def _run(self, coin_ids: str) -> str:
        # 1. Parse comma-separated coin IDs
        # 2. Call CoinGecko simple/price endpoint
        # 3. Extract price, 24h change, market cap, volume
        # 4. Format as structured string per coin
        # 5. Handle timeout + empty response + API errors
```

Returns: price, 24h direction + percentage, market cap in billions, volume in millions — per coin.

---

## Error Handling

Both tools handle three failure modes explicitly:

- **City not found** — geocoding returns no results, tool returns a clear message instead of crashing
- **API timeout** — 6–10 second timeout on all requests, returns readable error message
- **Unexpected API response** — try/except wraps all JSON parsing, fallback messages for each field

The agent receives the error message as tool output and incorporates it into the response rather than throwing an unhandled exception.

---

## Advanced Settings

**Analysis Depth** — Brief / Standard / Detailed controls instruction length passed to the agent's task description.

**Target Audience** — General / Investor / Business Analyst / Travel Planner adjusts tone instruction in the agent's backstory.

**Actionable Recommendations** — Toggle whether the agent includes specific next-step recommendations in output.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Agent Framework | CrewAI |
| Weather API | Open-Meteo (free, no key) |
| Crypto API | CoinGecko public API (free, no key) |
| HTTP Client | requests |
| Primary LLM | Gemini 2.5 Flash |
| Fallback LLM | Groq LLaMA 3.3 70B |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

---

## Local Setup

```bash
git clone https://github.com/sihabsafin/agent-forge
cd crewai-day5-real-apis

pip install crewai[google-genai] google-generativeai litellm streamlit requests

export GEMINI_API_KEY=your_key    # aistudio.google.com/apikey
export GROQ_API_KEY=your_key      # console.groq.com/keys (optional fallback)

streamlit run app.py
```

No additional API keys needed — Open-Meteo and CoinGecko are both open public APIs.

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

## Progression: Day 1 → Day 5

| | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 |
|---|---|---|---|---|---|
| Data source | LLM memory | LLM memory | LLM memory | Mock dict | Live APIs |
| Tools | None | None | None | 3 mock | 2 real |
| External calls | None | None | None | None | HTTP requests |
| Output accuracy | Estimated | Estimated | Estimated | Hardcoded | Real-time |
| Agent pattern | Single | Sequential | Hierarchical | Sequential | Sequential |

The shift at Day 5 is not about architecture — it's about credibility. An agent that says "Bitcoin is $67,432" because it fetched that number is fundamentally different from one that estimates it.

---

## Known Limitations

- CoinGecko's free public API has rate limits (~10–30 requests/minute) — consecutive rapid runs may return empty responses; wait 15–30 seconds between runs
- Open-Meteo is highly available but occasionally slow — 6-second timeout may trigger on congested connections
- Weather condition interpretation uses WMO weather codes mapped manually — edge cases may return "Unknown"
- This is a learning project — not connected to trading systems, financial advisors, or production data pipelines

---

*Part of `agent-forge` — a 15-day progressive build of multi-agent AI systems using CrewAI, from single-agent patterns to full real-world integrations.*
