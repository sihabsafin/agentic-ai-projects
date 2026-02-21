import streamlit as st
import os
import time
import json
import uuid
from datetime import datetime

st.set_page_config(
    page_title="AgentForge · Memory Systems",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Secrets ─────────────────────────────────────────────────────────────────────
for secret_key in ["GEMINI_API_KEY", "GROQ_API_KEY"]:
    try:
        os.environ[secret_key] = st.secrets[secret_key]
    except Exception:
        pass
os.environ.setdefault("OPENAI_API_KEY", "dummy-not-used")

# ── CSS ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:         #0d0f14;
    --surface:    #13161e;
    --surface2:   #1a1e2a;
    --surface3:   #222736;
    --border:     #2a2f3f;
    --border2:    #3a4156;
    --text:       #e8eaf0;
    --muted:      #6b7592;
    --muted2:     #4a5270;
    --accent:     #7c6af7;
    --accent2:    #9c8ffa;
    --accent-bg:  rgba(124,106,247,0.12);
    --accent-glow:rgba(124,106,247,0.25);
    --teal:       #2dd4bf;
    --teal-bg:    rgba(45,212,191,0.10);
    --amber:      #f59e0b;
    --amber-bg:   rgba(245,158,11,0.10);
    --green:      #34d399;
    --green-bg:   rgba(52,211,153,0.10);
    --red:        #f87171;
    --red-bg:     rgba(248,113,113,0.10);
    --serif:      'DM Serif Display', Georgia, serif;
    --mono:       'DM Mono', monospace;
    --sans:       'DM Sans', sans-serif;
    --r:          10px;
    --r-sm:       6px;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.8rem 5rem; max-width: 900px; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ── Topbar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: center; gap: 0.8rem; }
.brand-glyph {
    width: 36px; height: 36px; border-radius: 9px;
    background: linear-gradient(135deg, var(--accent), #5b4fd4);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 700; color: white;
    box-shadow: 0 0 20px var(--accent-glow);
}
.brand-text { display: flex; flex-direction: column; gap: 1px; }
.brand-name { font-size: 0.95rem; font-weight: 600; color: var(--text); letter-spacing: -0.01em; }
.brand-sub  { font-size: 0.68rem; color: var(--muted); letter-spacing: 0.05em; text-transform: uppercase; }
.day-badge {
    font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
    color: var(--accent2); background: var(--accent-bg);
    border: 1px solid rgba(124,106,247,0.3);
    padding: 0.3rem 0.75rem; border-radius: 999px;
    letter-spacing: 0.03em;
}

/* ── Hero ── */
.hero { margin-bottom: 2.5rem; }
.hero-eyebrow {
    font-family: var(--mono); font-size: 0.72rem; color: var(--teal);
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.5rem;
}
.hero-title {
    font-family: var(--serif); font-size: 2.4rem; line-height: 1.1;
    color: var(--text); margin: 0 0 0.75rem 0;
    background: linear-gradient(135deg, var(--text) 60%, var(--muted));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 0.95rem; color: var(--muted); line-height: 1.6; max-width: 560px;
}

/* ── Section heading ── */
.sec-label {
    font-family: var(--mono); font-size: 0.68rem; color: var(--muted);
    letter-spacing: 0.1em; text-transform: uppercase;
    margin: 0 0 0.45rem; display: block;
}

/* ── Mode tabs ── */
.stRadio > div { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.stRadio > div > label {
    flex: 1; min-width: 140px;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 0.75rem 1rem !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    font-size: 0.85rem !important;
    color: var(--muted) !important;
}
.stRadio > div > label:hover {
    border-color: var(--accent) !important;
    color: var(--text) !important;
    background: var(--accent-bg) !important;
}
.stRadio > div > label[data-checked="true"],
.stRadio > div > label[aria-checked="true"] {
    border-color: var(--accent) !important;
    background: var(--accent-bg) !important;
    color: var(--accent2) !important;
}
.stRadio > div > label > div { display: none !important; }
.stRadio > div > label > div + div { display: block !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── Button ── */
.stButton > button {
    width: 100%; background: linear-gradient(135deg, var(--accent), #5b4fd4) !important;
    color: white !important; border: none !important;
    border-radius: var(--r) !important; padding: 0.85rem 2rem !important;
    font-family: var(--sans) !important; font-weight: 600 !important;
    font-size: 0.9rem !important; letter-spacing: 0.01em !important;
    cursor: pointer !important; transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px var(--accent-glow) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px var(--accent-glow) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Divider ── */
.div { height: 1px; background: var(--border); margin: 1.5rem 0; }

/* ── Memory vault ── */
.vault-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1rem;
}
.vault-title {
    display: flex; align-items: center; gap: 0.6rem;
    font-size: 0.85rem; font-weight: 600; color: var(--text);
}
.vault-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--teal); box-shadow: 0 0 8px var(--teal);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.85); }
}
.vault-count {
    font-family: var(--mono); font-size: 0.72rem;
    color: var(--muted); background: var(--surface2);
    border: 1px solid var(--border); border-radius: 999px;
    padding: 0.15rem 0.6rem;
}

.memory-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 1rem 1.1rem;
    margin-bottom: 0.6rem; position: relative;
    transition: border-color 0.15s ease;
}
.memory-card:hover { border-color: var(--border2); }
.memory-card-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.4rem;
}
.memory-tag {
    font-family: var(--mono); font-size: 0.68rem; font-weight: 500;
    padding: 0.2rem 0.55rem; border-radius: 4px;
    letter-spacing: 0.03em;
}
.tag-market  { background: var(--accent-bg); color: var(--accent2); border: 1px solid rgba(124,106,247,0.25); }
.tag-tech    { background: var(--teal-bg);   color: var(--teal);    border: 1px solid rgba(45,212,191,0.25); }
.tag-general { background: var(--amber-bg);  color: var(--amber);   border: 1px solid rgba(245,158,11,0.25); }
.tag-health  { background: var(--green-bg);  color: var(--green);   border: 1px solid rgba(52,211,153,0.25); }
.tag-custom  { background: var(--surface2);  color: var(--muted2);  border: 1px solid var(--border); }

.memory-ts {
    font-family: var(--mono); font-size: 0.68rem; color: var(--muted2);
}
.memory-text { font-size: 0.88rem; color: var(--text); line-height: 1.55; }
.memory-id   { font-family: var(--mono); font-size: 0.65rem; color: var(--muted2); margin-top: 0.4rem; }

/* ── Query results ── */
.result-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 1.2rem;
    margin-bottom: 0.7rem;
}
.result-header {
    display: flex; align-items: center; gap: 0.6rem;
    margin-bottom: 0.6rem;
}
.result-rank {
    font-family: var(--mono); font-size: 0.72rem; font-weight: 600;
    background: var(--accent-bg); color: var(--accent2);
    border: 1px solid rgba(124,106,247,0.3);
    width: 24px; height: 24px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.result-score {
    font-family: var(--mono); font-size: 0.72rem; color: var(--muted);
}
.score-bar {
    height: 3px; border-radius: 2px; margin-top: 0.3rem;
    background: linear-gradient(90deg, var(--accent), var(--teal));
    transition: width 0.5s ease;
}
.result-text { font-size: 0.88rem; color: var(--text); line-height: 1.55; }

/* ── Log ── */
.log-wrap {
    background: #0a0c12; border: 1px solid var(--border);
    border-radius: var(--r); overflow: hidden; margin-bottom: 1.5rem;
    font-family: var(--mono);
}
.log-head {
    display: flex; align-items: center; gap: 0.4rem;
    padding: 0.7rem 1rem; border-bottom: 1px solid var(--border);
    background: var(--surface);
}
.log-head-title { font-size: 0.72rem; color: var(--muted); margin-left: 0.4rem; letter-spacing: 0.05em; }
.log-body { padding: 0.8rem 1rem; max-height: 240px; overflow-y: auto; }
.log-line { display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.25rem; font-size: 0.75rem; }
.log-t    { color: var(--muted2); min-width: 44px; }
.log-tag  { font-size: 0.65rem; font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 3px; letter-spacing: 0.05em; min-width: 50px; text-align: center; }
.log-msg  { color: #b0bac8; }
.t-sys    { background: var(--surface3); color: var(--muted); border: 1px solid var(--border2); }
.t-mem    { background: var(--accent-bg); color: var(--accent2); border: 1px solid rgba(124,106,247,0.3); }
.t-agent  { background: var(--teal-bg);   color: var(--teal);    border: 1px solid rgba(45,212,191,0.25); }
.t-ok     { background: var(--green-bg);  color: var(--green);   border: 1px solid rgba(52,211,153,0.2); }
.t-err    { background: var(--red-bg);    color: var(--red);     border: 1px solid rgba(248,113,113,0.2); }

/* ── Output panel ── */
.output-panel {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); overflow: hidden; margin-top: 1.5rem;
}
.output-header {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.85rem 1.1rem;
    border-bottom: 1px solid var(--border);
    background: var(--surface2);
}
.output-icon {
    width: 26px; height: 26px; border-radius: 6px;
    background: var(--accent-bg); border: 1px solid rgba(124,106,247,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem;
}
.output-label { font-size: 0.82rem; font-weight: 600; color: var(--text); }
.output-body  { padding: 1.2rem 1.3rem; font-size: 0.88rem; color: #ccd2e0; line-height: 1.7; }
.output-body strong { color: var(--text); }
.output-body h1, .output-body h2, .output-body h3 { color: var(--text); font-family: var(--serif); margin-top: 1rem; }

/* ── Empty state ── */
.empty-vault {
    text-align: center; padding: 2.5rem 1rem;
    background: var(--surface); border: 1px dashed var(--border2);
    border-radius: var(--r);
}
.empty-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.empty-label { font-size: 0.85rem; color: var(--muted); }

/* ── Stats row ── */
.stat-row { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }
.stat-card {
    flex: 1; background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 0.9rem 1rem;
}
.stat-val  { font-family: var(--mono); font-size: 1.4rem; font-weight: 600; color: var(--text); }
.stat-lbl  { font-size: 0.72rem; color: var(--muted); margin-top: 0.2rem; }

/* ── Insight presets ── */
.preset-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem; }
.preset-btn {
    font-size: 0.78rem; color: var(--muted);
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 999px; padding: 0.3rem 0.75rem;
    cursor: pointer; transition: all 0.15s;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
    font-size: 0.85rem !important;
}

/* Alert */
.err-box {
    background: var(--red-bg); border: 1px solid rgba(248,113,113,0.3);
    border-radius: var(--r-sm); padding: 0.9rem 1rem;
    font-size: 0.85rem; color: var(--red); margin-top: 1rem;
}
.info-box {
    background: var(--accent-bg); border: 1px solid rgba(124,106,247,0.3);
    border-radius: var(--r-sm); padding: 0.9rem 1rem;
    font-size: 0.85rem; color: var(--accent2); margin-top: 1rem;
}

/* Multiselect tag */
.stMultiSelect span[data-baseweb="tag"] {
    background: var(--accent-bg) !important;
    border: 1px solid rgba(124,106,247,0.3) !important;
    color: var(--accent2) !important;
}

/* Select slider */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] { color: var(--muted) !important; }

</style>
""", unsafe_allow_html=True)


# ── Topbar ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="brand">
        <div class="brand-glyph">◈</div>
        <div class="brand-text">
            <span class="brand-name">AgentForge</span>
            <span class="brand-sub">15-Day Build Series</span>
        </div>
    </div>
    <div class="day-badge">DAY 6 · MEMORY SYSTEMS</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">SHORT-TERM + LONG-TERM · VECTOR RETRIEVAL</div>
    <h1 class="hero-title">Agents with Memory</h1>
    <p class="hero-sub">
        Store business insights in a vector database (ChromaDB). Query by semantic
        similarity. Deploy a strategist agent that <em>recalls</em> stored knowledge
        before recommending what AI business to launch.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Init session state ────────────────────────────────────────────────────────────
if "chroma_collection" not in st.session_state:
    st.session_state["chroma_collection"] = None
if "memory_entries" not in st.session_state:
    st.session_state["memory_entries"] = []  # [{id, text, category, ts}]
if "chroma_ready" not in st.session_state:
    st.session_state["chroma_ready"] = False


# ── Init ChromaDB (lazy) ──────────────────────────────────────────────────────────
@st.cache_resource
def init_chroma():
    try:
        import chromadb
        client = chromadb.Client()
        collection = client.get_or_create_collection(
            name="business_memory",
            metadata={"hnsw:space": "cosine"}
        )
        return collection, None
    except ImportError:
        return None, "chromadb not installed. Add `chromadb` to requirements.txt."
    except Exception as e:
        return None, str(e)


collection, chroma_err = init_chroma()
if collection is not None:
    st.session_state["chroma_collection"] = collection
    st.session_state["chroma_ready"] = True


# ── Memory status banner ──────────────────────────────────────────────────────────
if chroma_err:
    st.markdown(f'<div class="err-box">⚠ ChromaDB Error: {chroma_err}</div>', unsafe_allow_html=True)
    st.stop()


# ── Stats row ─────────────────────────────────────────────────────────────────────
entry_count = len(st.session_state["memory_entries"])
categories  = list(set(e["category"] for e in st.session_state["memory_entries"])) if entry_count > 0 else []

st.markdown(f"""
<div class="stat-row">
    <div class="stat-card">
        <div class="stat-val">{entry_count}</div>
        <div class="stat-lbl">Memories stored</div>
    </div>
    <div class="stat-card">
        <div class="stat-val">{len(categories)}</div>
        <div class="stat-lbl">Categories</div>
    </div>
    <div class="stat-card">
        <div class="stat-val">{"LIVE" if st.session_state["chroma_ready"] else "OFF"}</div>
        <div class="stat-lbl">ChromaDB status</div>
    </div>
    <div class="stat-card">
        <div class="stat-val">cosine</div>
        <div class="stat-lbl">Similarity metric</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📥  Store Memory", "🔍  Query Memory", "🤖  Strategist Agent"])


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 1 — STORE MEMORY
# ══════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
    st.markdown('<span class="sec-label">Insight Category</span>', unsafe_allow_html=True)
    category = st.selectbox(
        "cat", ["Market", "Technology", "Health", "General", "Custom"],
        label_visibility="collapsed"
    )

    st.markdown('<span class="sec-label">Business Insight</span>', unsafe_allow_html=True)
    insight_text = st.text_area(
        "insight",
        placeholder="e.g. AI-powered fitness coaching apps projected to grow at 28% CAGR through 2028, driven by wearable adoption and personalized health data trends.",
        height=110,
        label_visibility="collapsed"
    )

    # Presets
    PRESETS = [
        ("AI SaaS", "Global AI SaaS market projected to exceed $1 trillion by 2030, with SME adoption growing 3× faster than enterprise."),
        ("Edtech", "AI tutoring platforms show 4× better retention rates vs traditional e-learning; underserved in emerging markets."),
        ("Fitness", "AI fitness market estimated at $20B globally. Personalized coaching and injury prevention drive highest LTV."),
        ("Fintech", "AI fraud detection reduces false positives by 60% vs rule-based systems; banks paying $500K+ per integration."),
        ("Healthcare", "LLM-powered clinical note generation reduces physician admin time by 2 hrs/day. Regulatory path clearest in US."),
        ("E-commerce", "AI product recommendation engines increase average order value by 35%; top ROI use case for mid-market retailers."),
    ]
    st.markdown('<span class="sec-label">Quick Presets</span>', unsafe_allow_html=True)
    preset_cols = st.columns(3)
    for i, (label, _) in enumerate(PRESETS):
        with preset_cols[i % 3]:
            if st.button(label, key=f"preset_{i}"):
                st.session_state["preset_text"] = PRESETS[i][1]
                st.rerun()

    # Apply preset
    if "preset_text" in st.session_state and st.session_state["preset_text"]:
        insight_text = st.session_state["preset_text"]
        st.session_state["preset_text"] = ""

    if st.button("◈  ADD TO MEMORY VAULT", key="add_btn"):
        if not insight_text.strip():
            st.markdown('<div class="err-box">⚠ Please enter an insight before storing.</div>', unsafe_allow_html=True)
        else:
            coll = st.session_state["chroma_collection"]
            doc_id = f"mem_{uuid.uuid4().hex[:8]}"
            try:
                coll.add(
                    documents=[insight_text.strip()],
                    metadatas=[{"category": category, "ts": datetime.now().isoformat()}],
                    ids=[doc_id]
                )
                st.session_state["memory_entries"].append({
                    "id": doc_id,
                    "text": insight_text.strip(),
                    "category": category,
                    "ts": datetime.now().strftime("%H:%M:%S")
                })
                st.success(f"✓ Stored as `{doc_id}` in ChromaDB")
            except Exception as e:
                st.markdown(f'<div class="err-box">ChromaDB write error: {e}</div>', unsafe_allow_html=True)

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)

    # Memory vault display
    entries = st.session_state["memory_entries"]
    vault_count = len(entries)

    st.markdown(f"""
    <div class="vault-header">
        <div class="vault-title">
            <div class="vault-dot"></div>
            Memory Vault
        </div>
        <span class="vault-count">{vault_count} document{"s" if vault_count != 1 else ""}</span>
    </div>
    """, unsafe_allow_html=True)

    if not entries:
        st.markdown("""
        <div class="empty-vault">
            <div class="empty-icon">🗄️</div>
            <div class="empty-label">No memories stored yet. Add insights above or use a Quick Preset.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        tag_cls_map = {"Market": "tag-market", "Technology": "tag-tech",
                       "General": "tag-general", "Health": "tag-health", "Custom": "tag-custom"}
        for e in reversed(entries):
            cls = tag_cls_map.get(e["category"], "tag-custom")
            st.markdown(f"""
            <div class="memory-card">
                <div class="memory-card-header">
                    <span class="memory-tag {cls}">{e["category"].upper()}</span>
                    <span class="memory-ts">{e["ts"]}</span>
                </div>
                <div class="memory-text">{e["text"]}</div>
                <div class="memory-id">{e["id"]}</div>
            </div>
            """, unsafe_allow_html=True)

    if vault_count > 0:
        if st.button("🗑  Clear all memories", key="clear_btn"):
            try:
                coll = st.session_state["chroma_collection"]
                all_ids = [e["id"] for e in st.session_state["memory_entries"]]
                if all_ids:
                    coll.delete(ids=all_ids)
                st.session_state["memory_entries"] = []
                st.rerun()
            except Exception as ex:
                st.markdown(f'<div class="err-box">Clear error: {ex}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 2 — QUERY MEMORY
# ══════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    entries_count = len(st.session_state["memory_entries"])
    if entries_count == 0:
        st.markdown("""
        <div class="info-box">ℹ  No memories stored yet. Go to the <strong>Store Memory</strong> tab and add at least 3 insights first.</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<span class="sec-label">Semantic Search Query</span>', unsafe_allow_html=True)
        query_text = st.text_input(
            "query",
            placeholder="e.g. What AI business has the best market opportunity?",
            label_visibility="collapsed"
        )

        col_n, col_cat = st.columns(2)
        with col_n:
            st.markdown('<span class="sec-label">Top-N Results</span>', unsafe_allow_html=True)
            n_results = st.slider("n", 1, min(entries_count, 5), min(3, entries_count), label_visibility="collapsed")
        with col_cat:
            st.markdown('<span class="sec-label">Filter by Category</span>', unsafe_allow_html=True)
            all_cats = list(set(e["category"] for e in st.session_state["memory_entries"]))
            filter_cats = st.multiselect("fcat", ["All"] + all_cats, default=["All"], label_visibility="collapsed")

        if st.button("🔍  SEARCH MEMORY", key="query_btn"):
            if not query_text.strip():
                st.markdown('<div class="err-box">⚠ Please enter a query.</div>', unsafe_allow_html=True)
            else:
                coll = st.session_state["chroma_collection"]
                try:
                    where_filter = None
                    if filter_cats and "All" not in filter_cats:
                        if len(filter_cats) == 1:
                            where_filter = {"category": filter_cats[0]}
                        else:
                            where_filter = {"category": {"$in": filter_cats}}

                    results = coll.query(
                        query_texts=[query_text.strip()],
                        n_results=n_results,
                        where=where_filter if where_filter else None,
                        include=["documents", "distances", "metadatas"]
                    )

                    docs      = results.get("documents", [[]])[0]
                    distances = results.get("distances", [[]])[0]
                    metas     = results.get("metadatas", [[]])[0]

                    if not docs:
                        st.markdown('<div class="info-box">No results found for that query.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="margin:0.75rem 0 0.5rem;font-size:0.8rem;color:var(--muted)">Found <strong style="color:var(--text)">{len(docs)}</strong> results for: <em style="color:var(--accent2)">{query_text.strip()}</em></div>', unsafe_allow_html=True)
                        tag_cls_map = {"Market": "tag-market", "Technology": "tag-tech",
                                       "General": "tag-general", "Health": "tag-health", "Custom": "tag-custom"}
                        for i, (doc, dist, meta) in enumerate(zip(docs, distances, metas)):
                            # cosine: distance 0 = identical. similarity = 1 - distance
                            similarity = max(0, round((1 - dist) * 100, 1))
                            bar_width  = int(similarity)
                            cat        = meta.get("category", "General")
                            cls        = tag_cls_map.get(cat, "tag-custom")
                            st.markdown(f"""
                            <div class="result-card">
                                <div class="result-header">
                                    <div class="result-rank">#{i+1}</div>
                                    <span class="memory-tag {cls}">{cat.upper()}</span>
                                    <span class="result-score">Similarity: {similarity}%</span>
                                </div>
                                <div class="score-bar" style="width:{bar_width}%"></div>
                                <div class="result-text" style="margin-top:0.6rem">{doc}</div>
                            </div>
                            """, unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f'<div class="err-box">Query error: {e}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 3 — STRATEGIST AGENT
# ══════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    entries_count = len(st.session_state["memory_entries"])
    if entries_count < 3:
        st.markdown(f"""
        <div class="info-box">ℹ  You have <strong>{entries_count}</strong> memory entries.
        Add at least <strong>3 insights</strong> in the Store Memory tab so the agent
        has enough context to reason from.</div>
        """, unsafe_allow_html=True)
    else:
        # ── Model selector ───────────────────────────────────────────────────────
        MODELS = {
            "Gemini (Primary)": {
                "gemini/gemini-2.5-flash-preview-04-17": "Gemini 2.5 Flash",
                "gemini/gemini-2.0-flash":               "Gemini 2.0 Flash",
            },
            "Groq (Fallback)": {
                "groq/llama-3.3-70b-versatile": "LLaMA 3.3 70B",
                "groq/mixtral-8x7b-32768":      "Mixtral 8x7B",
            },
        }
        col_p, col_m = st.columns(2)
        with col_p:
            st.markdown('<span class="sec-label">Provider</span>', unsafe_allow_html=True)
            provider_choice = st.selectbox("prov", list(MODELS.keys()), label_visibility="collapsed", key="prov")
        with col_m:
            st.markdown('<span class="sec-label">Model</span>', unsafe_allow_html=True)
            model_opts = MODELS[provider_choice]
            model_id   = st.selectbox("mod", list(model_opts.keys()),
                                      format_func=lambda x: model_opts[x],
                                      label_visibility="collapsed", key="mod")

        is_gemini = model_id.startswith("gemini/")

        st.markdown('<div class="div"></div>', unsafe_allow_html=True)

        # ── Strategy question ────────────────────────────────────────────────────
        st.markdown('<span class="sec-label">Strategic Question</span>', unsafe_allow_html=True)
        strategy_q = st.text_area(
            "strat_q",
            value="Based on the stored insights, which AI business opportunity should I pursue first, and why?",
            height=90,
            label_visibility="collapsed"
        )

        with st.expander("⚙  Agent Settings"):
            analysis_depth = st.select_slider(
                "Analysis Depth", ["Brief", "Standard", "Detailed"], value="Standard"
            )
            focus = st.selectbox(
                "Strategic Focus",
                ["Market Opportunity", "Technical Feasibility", "Revenue Potential", "Competitive Moat", "Balanced"]
            )
            include_risks = st.checkbox("Include risk assessment", value=True)
            include_roadmap = st.checkbox("Include 90-day action plan", value=True)

        st.markdown('<div class="div"></div>', unsafe_allow_html=True)

        run_btn = st.button("◈  RECALL MEMORY & RUN STRATEGIST")

        if run_btn:
            # ── Import guard ─────────────────────────────────────────────────────
            try:
                from crewai import Agent, Task, Crew, LLM
                from crewai.tools import BaseTool
                from typing import ClassVar
            except ImportError as e:
                st.markdown(f'<div class="err-box">Import error: {e}</div>', unsafe_allow_html=True)
                st.stop()

            api_key = os.environ.get("GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY", "")
            if not api_key:
                key_name = "GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY"
                st.markdown(f'<div class="err-box">⚠ {key_name} not found in Streamlit Secrets.</div>', unsafe_allow_html=True)
                st.stop()

            t0 = time.time()
            log_ph    = st.empty()
            status_ph = st.empty()

            def ts():
                return f"{round(time.time()-t0,1):>5}s"

            def render_log(lines):
                rows = ""
                for t_str, tag, cls, msg in lines:
                    rows += (f'<div class="log-line">'
                             f'<span class="log-t">{t_str}</span>'
                             f'<span class="log-tag {cls}">{tag}</span>'
                             f'<span class="log-msg">{msg}</span></div>')
                log_ph.markdown(f"""
                <div class="log-wrap">
                    <div class="log-head">
                        <div style="width:8px;height:8px;border-radius:50%;background:#e06060"></div>
                        <div style="width:8px;height:8px;border-radius:50%;background:#f0a500"></div>
                        <div style="width:8px;height:8px;border-radius:50%;background:#7ec87e"></div>
                        <span class="log-head-title">Memory + Agent Execution Log</span>
                    </div>
                    <div class="log-body">{rows}</div>
                </div>""", unsafe_allow_html=True)

            log = []
            log.append((ts(), "SYS", "t-sys",
                        f"Provider: {'gemini' if is_gemini else 'groq'} · {model_id.split('/')[1]}"))
            log.append((ts(), "MEM", "t-mem",
                        f"ChromaDB ready · {entries_count} documents in vault"))
            render_log(log)

            # ── Build MemorySearchTool ────────────────────────────────────────────
            coll_ref = st.session_state["chroma_collection"]

            class MemorySearchTool(BaseTool):
                name: str = "Business Memory Search Tool"
                description: str = (
                    "Searches stored business insights using semantic similarity. "
                    "Use this tool FIRST to recall relevant market data, trends, and insights "
                    "before making any strategic recommendations. "
                    "Input: a question or topic as a string. "
                    "Output: top matching insights with similarity scores."
                )
                def _run(self, query: str) -> str:
                    try:
                        n = min(5, len(st.session_state["memory_entries"]))
                        if n == 0:
                            return "No memories stored yet."
                        results = coll_ref.query(
                            query_texts=[query.strip()],
                            n_results=n,
                            include=["documents", "distances", "metadatas"]
                        )
                        docs  = results.get("documents", [[]])[0]
                        dists = results.get("distances",  [[]])[0]
                        metas = results.get("metadatas",  [[]])[0]
                        if not docs:
                            return "No relevant memories found for that query."
                        lines = [f"Retrieved {len(docs)} relevant insights from memory vault:\n"]
                        for i, (doc, dist, meta) in enumerate(zip(docs, dists, metas)):
                            sim = max(0, round((1 - dist) * 100, 1))
                            cat = meta.get("category", "General")
                            lines.append(
                                f"[{i+1}] Category: {cat} | Similarity: {sim}%\n"
                                f"    Insight: {doc}\n"
                            )
                        return "\n".join(lines)
                    except Exception as e:
                        return f"Memory search error: {e}"

            memory_tool = MemorySearchTool()

            log.append((ts(), "MEM", "t-mem", "MemorySearchTool initialised"))
            render_log(log)

            # ── Build short-term memory context ──────────────────────────────────
            recent_entries = st.session_state["memory_entries"][-3:]
            recent_context = " | ".join([e["text"][:80] + "..." for e in recent_entries])

            # ── Agent depth instructions ──────────────────────────────────────────
            depth_map = {
                "Brief":    "Provide a concise 2-3 paragraph analysis.",
                "Standard": "Provide a thorough analysis with clear sections.",
                "Detailed": "Provide a comprehensive deep-dive with evidence from every retrieved memory.",
            }
            focus_map = {
                "Market Opportunity":    "Focus primarily on market size, timing, and growth potential.",
                "Technical Feasibility": "Focus primarily on technical complexity, build time, and skill requirements.",
                "Revenue Potential":     "Focus primarily on monetization models, pricing, and revenue projections.",
                "Competitive Moat":      "Focus primarily on defensibility, differentiation, and competitive advantages.",
                "Balanced":              "Provide a balanced analysis across market, technical, and revenue dimensions.",
            }

            risk_instruction    = " Include a risk section with top 3 risks and mitigations." if include_risks else ""
            roadmap_instruction = " Include a 90-day action plan with concrete milestones." if include_roadmap else ""

            log.append((ts(), "AGENT", "t-agent", "Building strategist agent..."))
            render_log(log)

            # ── LLM ──────────────────────────────────────────────────────────────
            try:
                llm = LLM(model=model_id, temperature=0.3)
            except Exception as e:
                st.markdown(f'<div class="err-box">LLM init error: {e}</div>', unsafe_allow_html=True)
                st.stop()

            # ── Agents ───────────────────────────────────────────────────────────
            memory_researcher = Agent(
                role="Memory Researcher",
                goal=(
                    "Retrieve and surface the most relevant business insights from the memory vault "
                    "to support the strategist's decision-making."
                ),
                backstory=(
                    "You are a meticulous research analyst who always searches the memory vault FIRST "
                    "before drawing conclusions. You never invent data — every claim you make is grounded "
                    "in a retrieved memory. You run multiple targeted queries to ensure comprehensive coverage."
                ),
                tools=[memory_tool],
                llm=llm,
                verbose=True,
                max_iter=4,
            )

            strategist = Agent(
                role="AI Business Strategist",
                goal=(
                    "Using retrieved memory insights, provide actionable strategic recommendations "
                    "on which AI business to launch and how."
                ),
                backstory=(
                    f"You are a senior AI business strategist with 15 years of experience. "
                    f"You rely exclusively on grounded insights — never hallucinate data. "
                    f"You communicate clearly and confidently. {focus_map[focus]}"
                ),
                tools=[memory_tool],
                llm=llm,
                verbose=True,
                max_iter=5,
            )

            # ── Tasks ─────────────────────────────────────────────────────────────
            recall_task = Task(
                description=(
                    f"Search the memory vault thoroughly to retrieve all insights relevant to: '{strategy_q}'. "
                    f"Run at least 3 different search queries covering: market opportunities, "
                    f"technology trends, and revenue models. Compile and present the retrieved insights clearly, "
                    f"noting the similarity score and category of each one."
                ),
                expected_output=(
                    "A structured compilation of 3-5 retrieved memory insights with their categories and similarity scores."
                ),
                agent=memory_researcher,
            )

            strategy_task = Task(
                description=(
                    f"Using ONLY the insights retrieved by the Memory Researcher, answer this strategic question: "
                    f"'{strategy_q}'\n\n"
                    f"{depth_map[analysis_depth]}{risk_instruction}{roadmap_instruction}\n\n"
                    f"Cite specific retrieved insights to support every recommendation. "
                    f"Never introduce data or statistics that were not in the retrieved memories."
                ),
                expected_output=(
                    "A structured strategic recommendation grounded entirely in retrieved memory insights."
                ),
                agent=strategist,
                context=[recall_task],
            )

            crew = Crew(
                agents=[memory_researcher, strategist],
                tasks=[recall_task, strategy_task],
                verbose=False,
            )

            log.append((ts(), "AGENT", "t-agent",
                        f"Crew assembled: Memory Researcher + Strategist · {analysis_depth} depth"))
            render_log(log)

            # ── Execute ──────────────────────────────────────────────────────────
            status_ph.markdown(
                '<div style="font-size:0.83rem;color:var(--muted);margin-bottom:1rem">'
                '⟳ Agents recalling memory and generating strategy...</div>',
                unsafe_allow_html=True
            )

            try:
                result = crew.kickoff()
                elapsed = round(time.time() - t0, 1)

                log.append((ts(), "MEM",  "t-mem",   "Memory recall complete"))
                log.append((ts(), "OK",   "t-ok",    f"Strategy generated in {elapsed}s"))
                render_log(log)
                status_ph.empty()

                # ── Output panel ─────────────────────────────────────────────────
                output_text = str(result).strip()
                st.markdown(f"""
                <div class="output-panel">
                    <div class="output-header">
                        <div class="output-icon">◈</div>
                        <span class="output-label">AI Strategist — Memory-Grounded Recommendation</span>
                    </div>
                    <div class="output-body">{output_text.replace(chr(10), '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)

                # ── Short-term memory recap ────────────────────────────────────────
                st.markdown("""
                <div style="margin-top:1.5rem;padding:1rem;background:var(--surface);
                     border:1px solid var(--border);border-radius:var(--r)">
                    <div style="font-size:0.75rem;color:var(--muted);margin-bottom:0.5rem;
                         font-family:var(--mono);letter-spacing:0.05em">
                        SHORT-TERM SESSION MEMORY — context shared between agents
                    </div>
                """, unsafe_allow_html=True)

                for task in [recall_task, strategy_task]:
                    agent_name = task.agent.role
                    task_out   = str(task.output).strip()[:300] if task.output else "—"
                    st.markdown(f"""
                    <div style="margin-bottom:0.5rem;padding:0.7rem 0.8rem;
                         background:var(--surface2);border-radius:6px">
                        <div style="font-size:0.7rem;color:var(--teal);font-family:var(--mono);
                             margin-bottom:0.3rem">{agent_name.upper()}</div>
                        <div style="font-size:0.8rem;color:var(--muted)">{task_out}...</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                log.append((ts(), "ERR", "t-err", str(e)[:80]))
                render_log(log)
                status_ph.empty()
                st.markdown(f'<div class="err-box">Agent execution error: {e}</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="div"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
     padding-top:0.5rem;font-size:0.72rem;color:var(--muted2);font-family:var(--mono)">
    <span>agent-forge · day 6 of 15</span>
    <span>chromadb · crewai · gemini 2.5 flash</span>
    <span>memory systems</span>
</div>
""", unsafe_allow_html=True)
