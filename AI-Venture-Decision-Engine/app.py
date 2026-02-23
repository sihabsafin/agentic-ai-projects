import streamlit as st
import os
import time
import json
import re

st.set_page_config(
    page_title="AgentForge · Investment Analyzer",
    page_icon="◎",
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
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #111318;
    --surface:   #181c22;
    --surface2:  #1e232c;
    --surface3:  #242a35;
    --border:    #262d3a;
    --border2:   #303a4a;
    --text:      #e2e8f0;
    --muted:     #5a6680;
    --muted2:    #7a8aa0;
    --accent:    #3b82f6;
    --accent-dim:#1e3a5f;
    --invest:    #10b981;
    --invest-dim:#052e1a;
    --consider:  #f59e0b;
    --consider-dim:#2d1f08;
    --reject:    #ef4444;
    --reject-dim:#2d0f0f;
    --serif:     'DM Serif Display', Georgia, serif;
    --mono:      'DM Mono', monospace;
    --sans:      'DM Sans', sans-serif;
    --shadow:    0 1px 4px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.4);
}

* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.8rem 5rem; max-width: 900px; }

/* ── Header ── */
.header {
    display: flex; align-items: flex-end; justify-content: space-between;
    padding-bottom: 1.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.header-left {}
.header-title {
    font-family: var(--serif);
    font-size: 1.7rem;
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}
.header-sub {
    font-family: var(--mono);
    font-size: 0.62rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.header-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.4rem; }
.day-badge {
    font-family: var(--mono);
    font-size: 0.58rem;
    font-weight: 500;
    color: var(--accent);
    background: var(--accent-dim);
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    letter-spacing: 0.08em;
}
.schema-badge {
    font-family: var(--mono);
    font-size: 0.58rem;
    color: var(--invest);
    background: var(--invest-dim);
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    letter-spacing: 0.06em;
}

/* ── Section label ── */
.slabel {
    font-family: var(--mono);
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    display: block;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
    caret-color: var(--accent) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
    background: var(--surface2) !important;
}
.stSelectbox div[data-baseweb="select"] {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
}

/* ── Button ── */
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    transition: all 0.15s !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.3) !important;
}
.stButton > button:hover {
    background: #2563eb !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Expander ── */
.stExpander { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; }
details summary { color: var(--muted2) !important; font-size: 0.8rem !important; font-family: var(--sans) !important; }

/* ── Divider ── */
.div { border: none; border-top: 1px solid var(--border); margin: 1.4rem 0; }

/* ── Schema preview box ── */
.schema-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.4rem;
}
.schema-box-head {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 1rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
}
.schema-box-title { font-family: var(--mono); font-size: 0.62rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
.schema-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
}
.schema-field {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.55rem 1rem;
    border-bottom: 1px solid var(--border);
    border-right: 1px solid var(--border);
}
.schema-field:nth-child(even) { border-right: none; }
.schema-field:nth-last-child(-n+2) { border-bottom: none; }
.sf-key { font-family: var(--mono); font-size: 0.65rem; color: var(--accent); }
.sf-type { font-family: var(--mono); font-size: 0.6rem; color: var(--muted); }
.sf-range { font-family: var(--mono); font-size: 0.58rem; color: var(--muted2); }

/* ── Status bar ── */
.status-bar {
    display: flex; align-items: center; gap: 0.8rem;
    padding: 0.7rem 1.1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 7px;
    margin-bottom: 1rem;
}
.s-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.s-run  { background: var(--consider); animation: blink 1.2s ease-in-out infinite; }
.s-done { background: var(--invest); }
.s-err  { background: var(--reject); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.s-text { font-family: var(--sans); font-size: 0.82rem; color: var(--text); flex: 1; }
.s-meta { font-family: var(--mono); font-size: 0.62rem; color: var(--muted); }

/* ── Log ── */
.log-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 7px;
    overflow: hidden;
    margin-bottom: 1rem;
    font-family: var(--mono);
}
.log-head {
    padding: 0.55rem 1rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 0.6rem;
}
.log-head-title { font-size: 0.6rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
.log-body { padding: 0.7rem 1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.log-line { display: flex; align-items: flex-start; gap: 0.7rem; font-size: 0.68rem; line-height: 1.5; }
.log-t { color: var(--muted); min-width: 48px; }
.log-tag { font-size: 0.55rem; font-weight: 500; padding: 0.1rem 0.4rem; border-radius: 3px; white-space: nowrap; margin-top: 0.15rem; letter-spacing: 0.04em; }
.t-sys  { background: var(--surface3); color: var(--muted2); }
.t-agt  { background: var(--accent-dim); color: #7cb3f7; }
.t-json { background: #0d2318; color: #5ec47e; }
.t-val  { background: #1a1505; color: #d4a030; }
.t-err  { background: #2a0808; color: #e07070; }
.log-msg { color: var(--text); }

/* ── Decision banner ── */
.decision-banner {
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
}
.db-invest  { background: var(--invest-dim); border: 1px solid #0d4a2a; }
.db-consider{ background: var(--consider-dim); border: 1px solid #4a3008; }
.db-reject  { background: var(--reject-dim); border: 1px solid #4a1010; }
.db-left {}
.db-label { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.35rem; color: var(--muted2); }
.db-decision {
    font-family: var(--serif);
    font-size: 2rem;
    line-height: 1;
    letter-spacing: -0.02em;
}
.db-invest .db-decision { color: var(--invest); }
.db-consider .db-decision { color: var(--consider); }
.db-reject .db-decision { color: var(--reject); }
.db-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.4rem; }
.db-confidence {
    font-family: var(--mono);
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
}
.conf-high { background: #052e1a; color: var(--invest); border: 1px solid #0d4a2a; }
.conf-med  { background: var(--consider-dim); color: var(--consider); border: 1px solid #4a3008; }
.conf-low  { background: var(--reject-dim); color: var(--reject); border: 1px solid #4a1010; }
.db-startup { font-family: var(--sans); font-size: 0.8rem; color: var(--muted2); max-width: 260px; text-align: right; line-height: 1.4; }

/* ── Score grid ── */
.score-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.8rem;
    margin-bottom: 1.2rem;
}
.score-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.1rem;
    position: relative;
    overflow: hidden;
}
.score-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
}
.sc-market::after  { background: var(--accent); }
.sc-finance::after { background: var(--invest); }
.sc-risk::after    { background: var(--reject); }

.score-label { font-family: var(--mono); font-size: 0.58rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem; }
.score-value {
    font-family: var(--serif);
    font-size: 2.2rem;
    line-height: 1;
    letter-spacing: -0.02em;
    margin-bottom: 0.4rem;
}
.sv-market  { color: var(--accent); }
.sv-finance { color: var(--invest); }
.sv-risk    { color: var(--reject); }

/* ── Score bar ── */
.score-bar-wrap {
    height: 4px;
    background: var(--surface3);
    border-radius: 2px;
    margin-bottom: 0.5rem;
    overflow: hidden;
}
.score-bar { height: 100%; border-radius: 2px; transition: width 0.6s ease; }
.sb-market  { background: var(--accent); }
.sb-finance { background: var(--invest); }
.sb-risk    { background: var(--reject); }
.score-summary { font-size: 0.72rem; color: var(--muted2); line-height: 1.5; }

/* ── Validation panel ── */
.val-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.2rem;
}
.val-head {
    padding: 0.65rem 1.1rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
}
.val-title { font-family: var(--mono); font-size: 0.62rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
.val-status-pass { font-family: var(--mono); font-size: 0.62rem; color: var(--invest); background: var(--invest-dim); padding: 0.15rem 0.5rem; border-radius: 3px; }
.val-status-fail { font-family: var(--mono); font-size: 0.62rem; color: var(--reject); background: var(--reject-dim); padding: 0.15rem 0.5rem; border-radius: 3px; }
.val-body { padding: 0.8rem 1.1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.val-row { display: flex; align-items: center; gap: 0.6rem; font-family: var(--mono); font-size: 0.68rem; }
.val-check-pass { color: var(--invest); }
.val-check-fail { color: var(--reject); }
.val-check-warn { color: var(--consider); }
.val-key { color: var(--muted2); }
.val-msg { color: var(--text); }

/* ── Actions list ── */
.actions-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.2rem;
}
.actions-head {
    padding: 0.65rem 1.1rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    font-family: var(--mono); font-size: 0.62rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase;
}
.actions-body { padding: 0.8rem 1.1rem; display: flex; flex-direction: column; gap: 0.5rem; }
.action-item { display: flex; align-items: flex-start; gap: 0.6rem; font-size: 0.82rem; color: var(--text); line-height: 1.5; }
.action-num { font-family: var(--mono); font-size: 0.65rem; color: var(--accent); background: var(--accent-dim); padding: 0.05rem 0.4rem; border-radius: 3px; min-width: 22px; text-align: center; margin-top: 2px; flex-shrink: 0; }

/* ── Raw JSON panel ── */
.json-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.2rem;
}
.json-head {
    padding: 0.65rem 1.1rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
}
.json-title { font-family: var(--mono); font-size: 0.62rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
.json-body {
    padding: 1rem 1.2rem;
    font-family: var(--mono);
    font-size: 0.72rem;
    line-height: 1.8;
    color: #a8b8c8;
    white-space: pre-wrap;
    word-break: break-word;
}
.jk { color: #7cb3f7; }
.jv-num { color: #f0a500; }
.jv-str { color: #7ec87e; }
.jv-arr { color: #e07070; }

/* ── Stats ── */
.stats-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.8rem 0 1.2rem; }
.stat { font-family: var(--mono); font-size: 0.6rem; color: var(--muted); background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 0.22rem 0.65rem; }
.stat b { color: var(--accent); }

/* ── Error ── */
.err-box {
    background: var(--reject-dim); border: 1px solid #4a1010; border-left: 3px solid var(--reject);
    border-radius: 7px; padding: 0.9rem 1.2rem;
    font-family: var(--mono); font-size: 0.72rem; color: #e09090; line-height: 1.6;
}

/* ── Comparison table ── */
.cmp-table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 0.72rem; }
.cmp-table th { background: var(--surface2); color: var(--muted); font-weight: 500; padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid var(--border); letter-spacing: 0.06em; font-size: 0.62rem; text-transform: uppercase; }
.cmp-table td { padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border); color: var(--text); }
.cmp-table tr:last-child td { border-bottom: none; }
.cmp-invest  { color: var(--invest); font-weight: 600; }
.cmp-consider{ color: var(--consider); font-weight: 600; }
.cmp-reject  { color: var(--reject); font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ─────────────────────────────────────────────────────────────────────
def extract_json(text: str) -> dict | None:
    """Production JSON extraction — strips markdown fences, finds outermost braces."""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            # Try to fix common LLM JSON issues
            fixed = match.group()
            fixed = re.sub(r',\s*}', '}', fixed)
            fixed = re.sub(r',\s*]', ']', fixed)
            try:
                return json.loads(fixed)
            except Exception:
                return None
    return None


def validate_output(data: dict) -> list:
    """Returns list of validation results — each is (icon, key, message, passed)."""
    results = []
    required_keys = ["market_score", "financial_score", "risk_score",
                     "final_decision", "confidence_level", "recommended_actions"]
    # Field presence checks
    for key in required_keys:
        if key in data:
            results.append(("✓", key, "present", True))
        else:
            results.append(("✗", key, "MISSING — required field", False))
    # Score range checks
    for score_key in ["market_score", "financial_score", "risk_score"]:
        if score_key in data:
            val = data[score_key]
            if isinstance(val, (int, float)) and 0 <= val <= 10:
                results.append(("✓", score_key, f"valid range: {val}/10", True))
            else:
                results.append(("✗", score_key, f"out of range: {val} (must be 0–10)", False))
    # Business logic: high risk → no Invest
    if "risk_score" in data and "final_decision" in data:
        rs = data["risk_score"]
        fd = str(data["final_decision"]).strip()
        if isinstance(rs, (int, float)) and rs > 8 and fd.lower() == "invest":
            results.append(("⚠", "risk+decision", f"CONFLICT — risk_score {rs} > 8 but decision is 'Invest'", False))
        elif isinstance(rs, (int, float)) and rs > 8:
            results.append(("✓", "risk+decision", f"consistent — high risk ({rs}) → not 'Invest'", True))
        else:
            results.append(("✓", "risk+decision", "risk/decision consistency check passed", True))
    # recommended_actions type check
    if "recommended_actions" in data:
        val = data["recommended_actions"]
        if isinstance(val, list) and len(val) > 0:
            results.append(("✓", "recommended_actions", f"{len(val)} actions returned", True))
        else:
            results.append(("⚠", "recommended_actions", "empty or not a list", False))
    return results


def score_color(score, key_type):
    """Returns CSS class for score value."""
    if key_type == "risk":
        return "sv-risk"
    elif key_type == "market":
        return "sv-market"
    else:
        return "sv-finance"


def decision_class(decision: str) -> str:
    d = decision.lower().strip()
    if "invest" in d and "consider" not in d:
        return "db-invest"
    elif "consider" in d:
        return "db-consider"
    return "db-reject"


def confidence_class(conf: str) -> str:
    c = conf.lower().strip()
    if c == "high":
        return "conf-high"
    elif c == "medium" or c == "med":
        return "conf-med"
    return "conf-low"


def render_json_colored(data: dict) -> str:
    """Render colorized JSON for the raw output panel."""
    lines = []
    lines.append("{")
    items = list(data.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        if isinstance(v, (int, float)):
            lines.append(f'  <span class="jk">"{k}"</span>: <span class="jv-num">{v}</span>{comma}')
        elif isinstance(v, list):
            lines.append(f'  <span class="jk">"{k}"</span>: [')
            for j, item in enumerate(v):
                item_comma = "," if j < len(v) - 1 else ""
                lines.append(f'    <span class="jv-arr">"{item}"</span>{item_comma}')
            lines.append(f'  ]{comma}')
        else:
            lines.append(f'  <span class="jk">"{k}"</span>: <span class="jv-str">"{v}"</span>{comma}')
    lines.append("}")
    return "\n".join(lines)


# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="header-left">
        <div class="header-title">Investment Analyzer</div>
        <div class="header-sub">Structured AI Output · JSON Schema · Validation Layer</div>
    </div>
    <div class="header-right">
        <div class="day-badge">DAY 8</div>
        <div class="schema-badge">STRICT JSON OUTPUT</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Schema preview ────────────────────────────────────────────────────────────
st.markdown("""
<div class="schema-box">
    <div class="schema-box-head">
        <span class="schema-box-title">Output Schema — enforced on every run</span>
        <span style="font-family:var(--mono);font-size:0.58rem;color:var(--invest);">8 fields · validated</span>
    </div>
    <div class="schema-fields">
        <div class="schema-field"><span class="sf-key">market_score</span><span class="sf-range">0–10</span></div>
        <div class="schema-field"><span class="sf-key">market_summary</span><span class="sf-type">string</span></div>
        <div class="schema-field"><span class="sf-key">financial_score</span><span class="sf-range">0–10</span></div>
        <div class="schema-field"><span class="sf-key">financial_summary</span><span class="sf-type">string</span></div>
        <div class="schema-field"><span class="sf-key">risk_score</span><span class="sf-range">0–10</span></div>
        <div class="schema-field"><span class="sf-key">risk_summary</span><span class="sf-type">string</span></div>
        <div class="schema-field"><span class="sf-key">final_decision</span><span class="sf-type">Invest / Consider / Reject</span></div>
        <div class="schema-field"><span class="sf-key">confidence_level</span><span class="sf-type">Low / Medium / High</span></div>
        <div class="schema-field" style="border-bottom:none;"><span class="sf-key">recommended_actions</span><span class="sf-type">string[]</span></div>
        <div class="schema-field" style="border-bottom:none;border-right:none;"><span class="sf-key">total_score</span><span class="sf-type">computed 0–10</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Presets ────────────────────────────────────────────────────────────────────
PRESETS = {
    "AI Logistics Optimizer": (
        "An AI-powered logistics optimization SaaS for mid-size e-commerce companies shipping 10,000–500,000 "
        "parcels/month. Uses ML to optimize carrier selection, predict delivery delays, reroute shipments in real-time, "
        "and reduce last-mile costs by 15–25%. Pricing: $2,000–$8,000/month per client. "
        "TAM: $75B global logistics tech market growing at 14% CAGR. "
        "Competitive moat: proprietary delay prediction model trained on 50M+ historical shipments."
    ),
    "AI Legal Document Analyzer": (
        "An AI contract intelligence SaaS for solo lawyers and boutique firms billing $200–$500/hr. "
        "Scans contracts in 60 seconds, flags risky clauses, suggests redlines, and benchmarks against "
        "industry templates. Pricing: $149/month flat. TAM: $12B LegalTech growing at 26% CAGR. "
        "Key risk: liability concerns if AI misses critical clause in a $10M deal."
    ),
    "AI Recruitment Screening Tool": (
        "An AI-powered candidate screening SaaS for HR teams at companies hiring 50–500 employees/year. "
        "Auto-screens resumes, scores candidates against job requirements, schedules interviews, and "
        "generates hiring manager briefings. Pricing: $500/month per active job posting. "
        "TAM: $28B recruitment tech. Key risk: bias liability and tightening AI hiring regulations in EU/US."
    ),
    "AI Crypto Trading Bot": (
        "A retail-facing AI crypto trading bot that executes algorithmic trades based on technical signals, "
        "sentiment analysis, and on-chain data. Subscription at $99/month + 0.5% performance fee. "
        "TAM: $2.3B crypto trading tools. "
        "Key risks: regulatory uncertainty across jurisdictions, extreme market volatility, "
        "liability for user losses, and intense competition from established quant firms."
    ),
    "Custom Startup Idea": "",
}

MODELS = {
    "Gemini (Recommended)": {
        "gemini/gemini-2.5-flash": "Gemini 2.5 Flash  ✓",
        "gemini/gemini-2.0-flash": "Gemini 2.0 Flash",
    },
    "Groq (Fallback)": {
        "groq/llama-3.3-70b-versatile": "LLaMA 3.3 70B",
        "groq/mixtral-8x7b-32768":      "Mixtral 8x7B",
    },
}

col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    st.markdown('<span class="slabel">Startup Idea</span>', unsafe_allow_html=True)
    preset = st.selectbox("preset", list(PRESETS.keys()), label_visibility="collapsed")
with col2:
    st.markdown('<span class="slabel">Provider</span>', unsafe_allow_html=True)
    prov = st.selectbox("prov", list(MODELS.keys()), label_visibility="collapsed")
with col3:
    st.markdown('<span class="slabel">Model</span>', unsafe_allow_html=True)
    model_opts = MODELS[prov]
    model_id = st.selectbox("mod", list(model_opts.keys()),
                             format_func=lambda x: model_opts[x], label_visibility="collapsed")

is_gemini = model_id.startswith("gemini/")

st.markdown('<span class="slabel">Startup Description</span>', unsafe_allow_html=True)
startup_idea = st.text_area("idea", value=PRESETS[preset], height=110,
    placeholder="Describe the startup in detail — market size, pricing, risks, competitive moat...",
    label_visibility="collapsed")

with st.expander("⚙  Advanced — Analyst Configuration"):
    col_a, col_b = st.columns(2)
    with col_a:
        analyst_persona = st.selectbox("Analyst Persona",
            ["Venture Capital Partner", "Angel Investor", "Private Equity Analyst", "Startup Accelerator"])
    with col_b:
        investment_stage = st.selectbox("Investment Stage",
            ["Pre-seed", "Seed", "Series A", "Series B+"])
    strictness = st.select_slider("Risk Tolerance", ["Conservative", "Balanced", "Aggressive"], value="Balanced")

st.markdown('<div class="div"></div>', unsafe_allow_html=True)

# ── Comparison mode toggle ─────────────────────────────────────────────────────
compare_mode = st.toggle("📊  Comparison Mode — analyze all 4 presets and compare", value=False)

run_btn = st.button("◎  RUN INVESTMENT ANALYSIS")


# ── JSON Schema ────────────────────────────────────────────────────────────────
JSON_SCHEMA = """{
  "market_score": <integer 0-10>,
  "market_summary": "<2-3 sentence market assessment>",
  "financial_score": <integer 0-10>,
  "financial_summary": "<2-3 sentence financial viability assessment>",
  "risk_score": <integer 0-10, where 10 = extreme risk>,
  "risk_summary": "<2-3 sentence risk assessment>",
  "final_decision": "<exactly one of: Invest / Consider / Reject>",
  "confidence_level": "<exactly one of: Low / Medium / High>",
  "recommended_actions": ["<action 1>", "<action 2>", "<action 3>", "<action 4>", "<action 5>"],
  "total_score": <float — calculated as (market_score + financial_score + (10 - risk_score)) / 3>
}"""

def build_task_description(idea, persona, stage, risk_tolerance):
    strictness_map = {
        "Conservative": "Apply strict conservative criteria. Risk score should heavily penalize uncertainty.",
        "Balanced": "Apply balanced criteria weighing upside and downside equally.",
        "Aggressive": "Apply growth-focused criteria. Accept higher risk for higher market opportunity.",
    }
    return f"""You are a {persona} evaluating a {stage} investment opportunity.
{strictness_map[risk_tolerance]}

Startup to evaluate:
{idea}

You MUST return ONLY valid JSON matching this exact schema. No text before or after the JSON. No markdown. No explanation.

{JSON_SCHEMA}

Rules:
- All scores must be integers between 0 and 10
- risk_score of 10 = extreme risk / near-certain failure
- final_decision must be exactly "Invest", "Consider", or "Reject" — no other values
- If risk_score > 8, final_decision MUST NOT be "Invest" — use "Consider" or "Reject"
- recommended_actions must be a JSON array of exactly 5 specific, actionable strings
- total_score must be calculated as: (market_score + financial_score + (10 - risk_score)) / 3
- Return ONLY the JSON object. Nothing else."""


def run_analysis(idea, model_id, api_key, persona, stage, risk_tolerance, is_gemini):
    """Run a single analysis and return (parsed_dict, raw_text, elapsed)."""
    from crewai import Agent, Task, Crew, LLM
    if is_gemini:
        os.environ["GEMINI_API_KEY"] = api_key
    t0 = time.time()
    llm = LLM(model=model_id, api_key=api_key, temperature=0.3)
    agent = Agent(
        role=persona,
        goal="Evaluate startup investment opportunities and return strictly formatted JSON analysis.",
        backstory=(
            f"You are a seasoned {persona} with 15+ years of experience evaluating {stage} deals. "
            f"You are known for rigorous, data-driven analysis and returning clean, structured reports. "
            f"You always return pure JSON — never prose, never markdown, never explanations."
        ),
        llm=llm,
        verbose=False,
    )
    task = Task(
        description=build_task_description(idea, persona, stage, risk_tolerance),
        expected_output="A single valid JSON object matching the defined schema exactly. No other text.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    raw = str(task.output.raw) if task.output else str(result)
    parsed = extract_json(raw)
    elapsed = round(time.time() - t0, 1)
    return parsed, raw, elapsed


def render_analysis(parsed: dict, startup_label: str, elapsed: float, model_id: str):
    """Render the full analysis UI for a single parsed result."""
    decision = str(parsed.get("final_decision", "Unknown")).strip()
    confidence = str(parsed.get("confidence_level", "Low")).strip()
    market_s  = parsed.get("market_score", 0)
    finance_s = parsed.get("financial_score", 0)
    risk_s    = parsed.get("risk_score", 0)
    total_s   = parsed.get("total_score", round((market_s + finance_s + (10 - risk_s)) / 3, 1))

    db_cls   = decision_class(decision)
    conf_cls = confidence_class(confidence)

    # Decision banner
    st.markdown(f"""
    <div class="decision-banner {db_cls}">
        <div class="db-left">
            <div class="db-label">Final Decision</div>
            <div class="db-decision">{decision}</div>
        </div>
        <div class="db-right">
            <span class="db-confidence {conf_cls}">Confidence: {confidence}</span>
            <span class="db-startup">{startup_label[:80]}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # Score grid
    st.markdown(f"""
    <div class="score-grid">
        <div class="score-card sc-market">
            <div class="score-label">Market Score</div>
            <div class="score-value sv-market">{market_s}<span style="font-family:var(--mono);font-size:0.9rem;color:var(--muted)">/10</span></div>
            <div class="score-bar-wrap"><div class="score-bar sb-market" style="width:{market_s*10}%"></div></div>
            <div class="score-summary">{parsed.get("market_summary","")[:140]}</div>
        </div>
        <div class="score-card sc-finance">
            <div class="score-label">Financial Score</div>
            <div class="score-value sv-finance">{finance_s}<span style="font-family:var(--mono);font-size:0.9rem;color:var(--muted)">/10</span></div>
            <div class="score-bar-wrap"><div class="score-bar sb-finance" style="width:{finance_s*10}%"></div></div>
            <div class="score-summary">{parsed.get("financial_summary","")[:140]}</div>
        </div>
        <div class="score-card sc-risk">
            <div class="score-label">Risk Score</div>
            <div class="score-value sv-risk">{risk_s}<span style="font-family:var(--mono);font-size:0.9rem;color:var(--muted)">/10</span></div>
            <div class="score-bar-wrap"><div class="score-bar sb-risk" style="width:{risk_s*10}%"></div></div>
            <div class="score-summary">{parsed.get("risk_summary","")[:140]}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Validation panel
    val_results = validate_output(parsed)
    all_pass = all(r[3] for r in val_results)
    val_status_html = f'<span class="val-status-pass">ALL CHECKS PASSED</span>' if all_pass else f'<span class="val-status-fail">VALIDATION ISSUES</span>'
    val_rows = ""
    for icon, key, msg, passed in val_results:
        icon_cls = "val-check-pass" if icon == "✓" else ("val-check-warn" if icon == "⚠" else "val-check-fail")
        val_rows += f'<div class="val-row"><span class="{icon_cls}">{icon}</span><span class="val-key">{key}</span><span class="val-msg">— {msg}</span></div>'

    st.markdown(f"""
    <div class="val-panel">
        <div class="val-head">
            <span class="val-title">Validation Layer</span>
            {val_status_html}
        </div>
        <div class="val-body">{val_rows}</div>
    </div>""", unsafe_allow_html=True)

    # Recommended actions
    actions = parsed.get("recommended_actions", [])
    if actions and isinstance(actions, list):
        action_items = ""
        for i, a in enumerate(actions[:7], 1):
            action_items += f'<div class="action-item"><span class="action-num">{i:02d}</span><span>{a}</span></div>'
        st.markdown(f"""
        <div class="actions-panel">
            <div class="actions-head">Recommended Actions</div>
            <div class="actions-body">{action_items}</div>
        </div>""", unsafe_allow_html=True)

    # Stats
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat">total score <b>{total_s}/10</b></div>
        <div class="stat">decision <b>{decision}</b></div>
        <div class="stat">confidence <b>{confidence}</b></div>
        <div class="stat">elapsed <b>{elapsed}s</b></div>
        <div class="stat">model <b>{model_id.split("/")[1]}</b></div>
    </div>""", unsafe_allow_html=True)

    # Raw JSON
    colored_json = render_json_colored(parsed)
    st.markdown(f"""
    <div class="json-panel">
        <div class="json-head">
            <span class="json-title">Raw JSON Output</span>
            <span style="font-family:var(--mono);font-size:0.58rem;color:var(--invest);">extracted + validated</span>
        </div>
        <div class="json-body">{colored_json}</div>
    </div>""", unsafe_allow_html=True)


# ── Run ──────────────────────────────────────────────────────────────────────
if run_btn:
    if not startup_idea.strip() and not compare_mode:
        st.markdown('<div class="err-box">⚠ Please enter a startup idea.</div>', unsafe_allow_html=True)
        st.stop()

    try:
        from crewai import Agent, Task, Crew, LLM
    except ImportError as e:
        st.markdown(f'<div class="err-box">Import error: {e}</div>', unsafe_allow_html=True)
        st.stop()

    api_key = os.environ.get("GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY", "")
    if not api_key:
        st.markdown(f'<div class="err-box">⚠ {"GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY"} not found.</div>', unsafe_allow_html=True)
        st.stop()

    persona = locals().get("analyst_persona", "Venture Capital Partner")
    stage   = locals().get("investment_stage", "Seed")
    strict  = locals().get("strictness", "Balanced")

    t0 = time.time()
    log_ph    = st.empty()
    status_ph = st.empty()

    def ts():
        return f"{round(time.time()-t0,1):>5}s"

    def render_log(lines):
        rows = ""
        for t, tag, cls, msg in lines:
            rows += f'<div class="log-line"><span class="log-t">{t}</span><span class="log-tag {cls}">{tag}</span><span class="log-msg">{msg}</span></div>'
        log_ph.markdown(f"""
        <div class="log-wrap">
            <div class="log-head"><span style="width:8px;height:8px;border-radius:50%;background:var(--invest);display:inline-block;margin-right:4px;"></span>
            <span class="log-head-title">Execution Log</span></div>
            <div class="log-body">{rows}</div>
        </div>""", unsafe_allow_html=True)

    provider_label = "gemini" if is_gemini else "groq"
    log = [(ts(), "SYS", "t-sys", f"Agent: {persona} · Stage: {stage} · Risk: {strict} · {provider_label}")]
    render_log(log)
    log.append((ts(), "AGT", "t-agt", "Analyst agent initialized with strict JSON output instructions"))
    render_log(log); time.sleep(0.3)
    log.append((ts(), "JSON", "t-json", f"Schema enforced: 10 fields · validation layer active"))
    render_log(log); time.sleep(0.3)

    status_ph.markdown("""
    <div class="status-bar">
        <div class="s-dot s-run"></div>
        <span class="s-text">Analyst running — enforcing JSON schema…</span>
    </div>""", unsafe_allow_html=True)

    if compare_mode:
        # Run all 4 preset ideas
        compare_results = []
        preset_ideas = {k: v for k, v in PRESETS.items() if v}

        for i, (name, idea) in enumerate(preset_ideas.items(), 1):
            log.append((ts(), "AGT", "t-agt", f"Analyzing [{i}/{len(preset_ideas)}]: {name}"))
            render_log(log)
            try:
                parsed, raw, elapsed = run_analysis(idea, model_id, api_key, persona, stage, strict, is_gemini)
                if parsed:
                    compare_results.append((name, parsed, elapsed))
                    decision = parsed.get("final_decision", "N/A")
                    log.append((ts(), "JSON", "t-json", f"{name} → {decision} · total: {parsed.get('total_score','N/A')}/10"))
                    render_log(log)
                    time.sleep(1.5)  # rate limit buffer
                else:
                    log.append((ts(), "ERR", "t-err", f"{name} → JSON extraction failed"))
                    render_log(log)
            except Exception as ex:
                log.append((ts(), "ERR", "t-err", f"{name} → {str(ex)[:60]}"))
                render_log(log)
                time.sleep(2)

        log.append((ts(), "VAL", "t-val", f"Comparison complete · {len(compare_results)}/{len(preset_ideas)} succeeded"))
        render_log(log)
        status_ph.markdown(f"""
        <div class="status-bar">
            <div class="s-dot s-done"></div>
            <span class="s-text">Comparison complete — {len(compare_results)} startups analyzed</span>
            <span class="s-meta">{round(time.time()-t0,1)}s</span>
        </div>""", unsafe_allow_html=True)

        # Comparison table
        if compare_results:
            rows = ""
            for name, data, _ in compare_results:
                dec = str(data.get("final_decision", "N/A")).strip()
                dec_cls = "cmp-invest" if dec == "Invest" else ("cmp-consider" if dec == "Consider" else "cmp-reject")
                rows += f"""<tr>
                    <td>{name}</td>
                    <td>{data.get("market_score","N/A")}</td>
                    <td>{data.get("financial_score","N/A")}</td>
                    <td>{data.get("risk_score","N/A")}</td>
                    <td>{data.get("total_score","N/A")}</td>
                    <td class="{dec_cls}">{dec}</td>
                    <td>{data.get("confidence_level","N/A")}</td>
                </tr>"""
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;overflow:hidden;margin-bottom:1.4rem;">
                <div style="padding:0.65rem 1.1rem;background:var(--surface2);border-bottom:1px solid var(--border);font-family:var(--mono);font-size:0.62rem;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;">Startup Comparison — {persona} · {stage}</div>
                <div style="overflow-x:auto;padding:0.5rem;">
                    <table class="cmp-table">
                        <thead><tr>
                            <th>Startup</th><th>Market</th><th>Finance</th><th>Risk</th>
                            <th>Total</th><th>Decision</th><th>Confidence</th>
                        </tr></thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
            </div>""", unsafe_allow_html=True)

            # Individual panels
            for name, data, elapsed in compare_results:
                st.markdown(f'<div style="font-family:var(--mono);font-size:0.65rem;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;margin:1.4rem 0 0.5rem;">◎ {name}</div>', unsafe_allow_html=True)
                render_analysis(data, name, elapsed, model_id)

    else:
        # Single analysis
        try:
            parsed, raw, elapsed = run_analysis(startup_idea, model_id, api_key, persona, stage, strict, is_gemini)
            total_t = round(time.time() - t0, 1)

            if parsed:
                log.append((ts(), "JSON", "t-json", "JSON extracted successfully ✓"))
                val_results = validate_output(parsed)
                all_pass = all(r[3] for r in val_results)
                log.append((ts(), "VAL", "t-val", f"Validation: {'ALL PASSED ✓' if all_pass else 'ISSUES FOUND — check validation panel'}"))
                log.append((ts(), "SYS", "t-sys", f"Complete · decision: {parsed.get('final_decision','N/A')} · {total_t}s"))
                render_log(log)

                status_ph.markdown(f"""
                <div class="status-bar">
                    <div class="s-dot s-done"></div>
                    <span class="s-text">Analysis complete — JSON validated · schema enforced</span>
                    <span class="s-meta">{total_t}s</span>
                </div>""", unsafe_allow_html=True)

                label = startup_idea[:80] + "..." if len(startup_idea) > 80 else startup_idea
                render_analysis(parsed, label, elapsed, model_id)

            else:
                log.append((ts(), "ERR", "t-err", "JSON extraction failed — raw output shown below"))
                render_log(log)
                status_ph.markdown("""
                <div class="status-bar">
                    <div class="s-dot s-err"></div>
                    <span class="s-text">JSON extraction failed — check raw output</span>
                </div>""", unsafe_allow_html=True)
                st.markdown(f'<div class="err-box">Could not extract valid JSON from agent output.\n\nRaw output:\n{raw[:1200]}</div>', unsafe_allow_html=True)

        except Exception as e:
            err_str = str(e)
            log.append((ts(), "ERR", "t-err", "Execution failed"))
            render_log(log)
            status_ph.empty()
            if "resource_exhausted" in err_str.lower() or "quota" in err_str.lower() or "429" in err_str:
                st.markdown('<div class="err-box"><b>Quota Exhausted (429)</b>\n\nSwitch to Gemini 2.5 Flash and wait 60s.</div>', unsafe_allow_html=True)
            elif "rate_limit" in err_str.lower():
                st.markdown('<div class="err-box"><b>Rate limit.</b> Wait 30–60s and retry.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="err-box"><b>Error:</b> {err_str}</div>', unsafe_allow_html=True)
