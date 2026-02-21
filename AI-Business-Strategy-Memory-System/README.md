# AI-Business-Strategy-Memory-System

AI agents that store knowledge in a vector database, retrieve it by semantic similarity, and ground every strategic recommendation in recalled facts — not LLM hallucinations.

Built as Day 6 of a 15-day CrewAI learning program — the day agents stopped forgetting everything between runs.

---

## What This Does

Three tabs, one cohesive system:

**Store Memory** — Write any business insight, assign a category (Market / Tech / Health / General / Custom), and store it in ChromaDB with a single click. Six quick presets are included so you can populate the vault in seconds. Every entry is persisted in-session with its document ID, category, and timestamp.

**Query Memory** — Enter a natural language question. ChromaDB converts it to a vector embedding and retrieves the top-N most semantically similar documents. Results display with similarity percentage bars so you can see exactly how well each memory matches your query. Filter by category. Adjust result count.

**Strategist Agent** — Two CrewAI agents run in sequence. The Memory Researcher runs 3+ targeted queries against the vault and compiles retrieved insights. The Strategist synthesizes those insights into a grounded recommendation. The agents share context through CrewAI's built-in short-term memory system. A session memory recap at the bottom shows exactly what each agent produced.

---

## What's Actually Happening Under the Hood

```
User stores insights
        │
        ▼
ChromaDB converts text → vector embeddings
Stores vectors + metadata in-memory collection
        │
        ▼
User queries / Agent queries
        │
        ▼
ChromaDB cosine similarity search
Returns top-N documents ranked by relevance
        │
        ▼
Strategist agent receives retrieved context
Writes recommendation grounded in real stored data
        │
        ▼
Short-term memory: CrewAI shares recall_task output
as context to strategy_task automatically
```

---

## The Core Day 6 Lesson

Memory splits into two layers:

**Short-term (session memory)**: CrewAI automatically passes the output of earlier tasks as `context` to later tasks. The Memory Researcher's compiled findings are visible to the Strategist without any extra code — this is context memory at the framework level.

**Long-term (persistent memory)**: ChromaDB stores documents outside the LLM's context window. It uses vector embeddings to retrieve by *meaning*, not keyword. An agent asking "what AI business has the best market timing?" retrieves documents about market size and growth trends — even if those documents never used the word "timing."

This separation is what makes agents trustworthy at scale. The LLM provides reasoning. The database provides facts.

---

## Memory Tool

```python
class MemorySearchTool(BaseTool):
    name = "Business Memory Search Tool"
    description = "Searches stored business insights using semantic similarity..."

    def _run(self, query: str) -> str:
        results = collection.query(
            query_texts=[query],
            n_results=5,
            include=["documents", "distances", "metadatas"]
        )
        # Returns ranked documents with similarity scores
        # Cosine distance → similarity = 1 - distance
```

The tool is attached to both agents. The Memory Researcher uses it to retrieve, the Strategist uses it to cross-check.

---

## Two-Agent Architecture

```
Memory Researcher
    goal:     retrieve relevant insights from vault
    tools:    MemorySearchTool
    runs:     3+ targeted queries
    outputs:  compiled insight list with scores

        ↓ context passed automatically by CrewAI

AI Business Strategist
    goal:     synthesize insights into actionable recommendation
    tools:    MemorySearchTool (for cross-checking)
    receives: Memory Researcher's compiled findings
    outputs:  grounded strategic recommendation
```

---

## Tech Stack

| Layer | Choice |
|---|---|
| Agent Framework | CrewAI |
| Vector Database | ChromaDB (in-memory) |
| Similarity Metric | Cosine distance |
| Primary LLM | Gemini 2.5 Flash |
| Fallback LLM | Groq LLaMA 3.3 70B |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

---

## Local Setup

```bash
git clone https://github.com/sihabsafin/agent-forge
cd crewai-day6-memory

pip install crewai[google-genai] google-generativeai litellm streamlit chromadb

export GEMINI_API_KEY=your_key    # aistudio.google.com/apikey
export GROQ_API_KEY=your_key      # console.groq.com/keys (optional)

streamlit run app.py
```

---

## Streamlit Cloud Deployment

```toml
# Settings → Secrets
GEMINI_API_KEY = "your_gemini_key"
GROQ_API_KEY   = "your_groq_key"
```

`requirements.txt`:
```
crewai[google-genai]
google-generativeai
litellm
streamlit
chromadb
```

The only new dependency vs Day 5 is `chromadb`.

---

## Day 6 Assignment — Completed

| Requirement | Status |
|---|---|
| Store at least 3 different business insights | ✓ 6 presets + custom input |
| Query different things | ✓ Full semantic search tab with filters |
| Clean formatted output per result | ✓ Similarity bars, category tags, ranked cards |
| Attach memory tool to strategist agent | ✓ Two agents, both with MemorySearchTool |
| Task: recommend best AI business to launch | ✓ Strategist agent grounded in recalled memory |

---

## Known Limitations

- ChromaDB runs in-memory — memories reset when the Streamlit session ends. For production persistence use `chromadb.PersistentClient(path="./db")`
- Minimum 3 stored insights required before the Strategist tab activates
- CoinGecko / Open-Meteo calls from Day 5 are not included in this build — Day 6 focuses purely on memory
- Embeddings use ChromaDB's default model (all-MiniLM-L6-v2 via sentence-transformers) — first run may be slow as the model downloads

---

## Progression: Day 1 → Day 6

| | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 |
|---|---|---|---|---|---|---|
| Data source | LLM memory | LLM memory | LLM memory | Mock dict | Live APIs | Vector DB |
| Tools | None | None | None | 3 mock | 2 real | Memory tool |
| Memory | None | None | None | None | None | ChromaDB + CrewAI context |
| Output accuracy | Estimated | Estimated | Estimated | Hardcoded | Real-time | Retrieved |

---

*Part of `agent-forge` — a 15-day progressive build of multi-agent AI systems using CrewAI.*
