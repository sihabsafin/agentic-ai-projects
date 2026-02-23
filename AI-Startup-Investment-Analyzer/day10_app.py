"""
app.py — Streamlit UI layer
============================
This file only handles UI.
All business logic lives in execution.py.
app.py calls run_startup_analysis() — nothing else from the backend.

Module graph:
  app.py
    └── execution.py
          ├── crew_setup.py
          │     ├── agents.py
          │     ├── tasks.py
          │     └── tools.py
          └── utils.py
"""

import streamlit as st
import os
import time
import json

st.set_page_config(
    page_title="AgentForge · Modular Analyzer",
    page_icon="⬢",
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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Roboto+Mono:wght@300;400;500&display=swap');

:root {
    --bg:          #f4f2ee;
    --canvas:      #faf9f6;
    --surface:     #ffffff;
    --surface2:    #f7f5f1;
    --border:      #e2ddd6;
    --border2:     #cec8be;
    --text:        #1c1a16;
    --muted:       #8c8276;
    --muted2:      #b0a898;
    --accent:      #1a44cc;
    --accent-bg:   #eef2ff;
    --accent-bdr:  #c7d4f8;
    --green:       #0e7a3c;
    --green-bg:    #edfaf3;
    --green-bdr:   #a8dfc0;
    --amber:       #9a5c00;
    --amber-bg:    #fff8ec;
    --amber-bdr:   #f5d490;
    --red:         #b82020;
    --red-bg:      #fff0f0;
    --red-bdr:     #f5b8b8;
    --grid:        rgba(0,0,0,0.04);
    --sans:        'Plus Jakarta Sans', sans-serif;
    --mono:        'Roboto Mono', monospace;
    --r:           8px;
    --shadow:      0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:   0 4px 16px rgba(0,0,0,0.08);
}

* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
}

/* Blueprint grid background */
body {
    background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 32px 32px;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.8rem 5rem; max-width: 920px; }

/* ── Top header ── */
.hdr {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 1.2rem 1.5rem;
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 1.4rem;
    box-shadow: var(--shadow);
}
.hdr-title {
    font-size: 1.3rem; font-weight: 700;
    color: var(--text); letter-spacing: -0.02em;
}
.hdr-sub {
    font-family: var(--mono); font-size: 0.6rem;
    color: var(--muted); letter-spacing: 0.08em;
    text-transform: uppercase; margin-top: 0.25rem;
}
.hdr-tags { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.5rem; }
.hdr-tag {
    font-family: var(--mono); font-size: 0.56rem; font-weight: 500;
    padding: 0.15rem 0.55rem; border-radius: 3px;
    letter-spacing: 0.06em; text-transform: uppercase;
}
.ht-blue   { background: var(--accent-bg); color: var(--accent); border: 1px solid var(--accent-bdr); }
.ht-green  { background: var(--green-bg);  color: var(--green);  border: 1px solid var(--green-bdr); }
.ht-amber  { background: var(--amber-bg);  color: var(--amber);  border: 1px solid var(--amber-bdr); }
.day-badge {
    font-family: var(--mono); font-size: 0.65rem; font-weight: 600;
    color: var(--surface); background: var(--text);
    padding: 0.25rem 0.7rem; border-radius: 4px;
    letter-spacing: 0.04em;
}

/* ── Architecture diagram ── */
.arch-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    overflow: hidden;
    margin-bottom: 1.4rem;
    box-shadow: var(--shadow);
}
.arch-head {
    padding: 0.65rem 1.2rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
}
.arch-title { font-family: var(--mono); font-size: 0.6rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
.arch-body { padding: 1.2rem 1.4rem; }

/* ── Module grid ── */
.module-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.7rem;
    margin-bottom: 1.4rem;
}
.module-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 0.9rem 1rem;
    box-shadow: var(--shadow);
    transition: box-shadow 0.15s;
    position: relative;
    overflow: hidden;
}
.module-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.mc-tools::before     { background: #3b82f6; }
.mc-agents::before    { background: #10b981; }
.mc-tasks::before     { background: #f59e0b; }
.mc-crew::before      { background: #8b5cf6; }
.mc-utils::before     { background: #06b6d4; }
.mc-execution::before { background: #f97316; }
.mc-app::before       { background: var(--text); }

.mc-filename {
    font-family: var(--mono); font-size: 0.65rem; font-weight: 500;
    color: var(--text); margin-bottom: 0.3rem;
    display: flex; align-items: center; gap: 0.4rem;
}
.mc-badge {
    font-family: var(--mono); font-size: 0.5rem; font-weight: 500;
    padding: 0.1rem 0.35rem; border-radius: 2px;
    text-transform: uppercase; letter-spacing: 0.06em;
}
.mb-py  { background: #fef3c7; color: #92400e; }
.mb-ui  { background: var(--accent-bg); color: var(--accent); }
.mb-core{ background: var(--green-bg); color: var(--green); }
.mc-desc { font-size: 0.75rem; color: var(--muted); line-height: 1.5; margin-bottom: 0.4rem; }
.mc-exports {
    display: flex; flex-wrap: wrap; gap: 0.3rem;
}
.mc-export {
    font-family: var(--mono); font-size: 0.55rem;
    color: var(--muted2); background: var(--surface2);
    border: 1px solid var(--border);
    padding: 0.1rem 0.4rem; border-radius: 3px;
}

/* ── Dependency flow ── */
.dep-flow {
    display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;
    padding: 0.8rem 1rem;
    background: var(--surface2);
    border-radius: 6px;
    font-family: var(--mono); font-size: 0.65rem;
    color: var(--muted);
}
.dep-file { color: var(--text); font-weight: 500; }
.dep-arrow { color: var(--muted2); }

/* ── Slabel ── */
.slabel {
    font-family: var(--mono); font-size: 0.58rem; color: var(--muted);
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 0.35rem; display: block;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 7px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(26,68,204,0.1) !important;
    background: white !important;
}
.stSelectbox div[data-baseweb="select"] {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 7px !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
}
.stNumberInput input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 7px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 0.88rem !important;
}

/* ── Button ── */
.stButton > button {
    background: var(--text) !important;
    color: white !important; border: none !important;
    border-radius: 7px !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important; font-weight: 600 !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    transition: all 0.15s !important;
    letter-spacing: -0.01em !important;
    box-shadow: var(--shadow-md) !important;
}
.stButton > button:hover {
    background: #333 !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
    transform: translateY(-1px) !important;
}

/* ── Expander ── */
.stExpander { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--r) !important; box-shadow: var(--shadow) !important; }
details summary { color: var(--muted) !important; font-size: 0.82rem !important; }

/* ── Divider ── */
.div { border: none; border-top: 1px solid var(--border); margin: 1.2rem 0; }

/* ── Execution log ── */
.exec-log {
    background: #1a1714;
    border-radius: var(--r);
    overflow: hidden;
    margin-bottom: 1rem;
    font-family: var(--mono);
}
.el-head {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.55rem 1rem;
    border-bottom: 1px solid #2a2418;
    background: #141210;
}
.el-dots { display: flex; gap: 5px; }
.el-dot  { width:8px; height:8px; border-radius:50%; }
.el-title { font-size: 0.58rem; color: #4a4038; letter-spacing: 0.12em; text-transform: uppercase; }
.el-body { padding: 0.7rem 1rem; display: flex; flex-direction: column; gap: 0.35rem; }
.el-line { display: flex; align-items: flex-start; gap: 0.65rem; font-size: 0.67rem; line-height: 1.5; }
.el-t   { color: #4a4038; min-width: 48px; }
.el-tag { font-size: 0.54rem; font-weight: 500; padding: 0.1rem 0.38rem; border-radius: 2px; white-space: nowrap; margin-top: 0.15rem; letter-spacing: 0.04em; }
.lt-sys { background: #1e1e16; color: #6a6050; }
.lt-mod { background: #0e1a28; color: #6a9fd8; }
.lt-ok  { background: #0a1e10; color: #5ec87e; }
.lt-err { background: #280a0a; color: #e07070; }
.lt-val { background: #1a1205; color: #d4a030; }
.lt-json{ background: #0a1a14; color: #50d4b0; }
.el-msg { color: #c8b898; }

/* ── Status ── */
.status-bar {
    display: flex; align-items: center; gap: 0.8rem;
    padding: 0.65rem 1.1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 7px;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}
.s-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.s-run { background: var(--amber); animation: spin 2s linear infinite; }
.s-ok  { background: var(--green); }
.s-err { background: var(--red); }
@keyframes spin { 0%{opacity:1} 50%{opacity:0.3} 100%{opacity:1} }
.s-text { font-size: 0.82rem; color: var(--text); flex: 1; font-weight: 500; }
.s-meta { font-family: var(--mono); font-size: 0.62rem; color: var(--muted); }

/* ── Result sections ── */
.result-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}
.rs-head {
    display: flex; align-items: center; gap: 0.7rem; flex-wrap: wrap;
    padding: 0.75rem 1.2rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
}
.rs-badge {
    font-family: var(--mono); font-size: 0.58rem; font-weight: 500;
    padding: 0.15rem 0.55rem; border-radius: 4px;
    letter-spacing: 0.04em;
}
.rb-blue  { background: var(--accent-bg); color: var(--accent); border: 1px solid var(--accent-bdr); }
.rb-green { background: var(--green-bg); color: var(--green); border: 1px solid var(--green-bdr); }
.rb-amber { background: var(--amber-bg); color: var(--amber); border: 1px solid var(--amber-bdr); }
.rb-red   { background: var(--red-bg); color: var(--red); border: 1px solid var(--red-bdr); }
.rs-title { font-size: 0.78rem; color: var(--muted); font-weight: 500; }
.rs-body  { padding: 1.1rem 1.3rem; }

/* ── Decision banner ── */
.decision-banner {
    border-radius: var(--r);
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.1rem;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 1rem;
}
.db-invest  { background: var(--green-bg); border: 1.5px solid var(--green-bdr); }
.db-consider{ background: var(--amber-bg); border: 1.5px solid var(--amber-bdr); }
.db-reject  { background: var(--red-bg);   border: 1.5px solid var(--red-bdr); }
.db-label { font-family: var(--mono); font-size: 0.58rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.3rem; }
.db-dec   { font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1; }
.db-invest  .db-dec { color: var(--green); }
.db-consider .db-dec{ color: var(--amber); }
.db-reject  .db-dec { color: var(--red); }
.db-right  { display: flex; flex-direction: column; align-items: flex-end; gap: 0.4rem; }
.db-conf   { font-family: var(--mono); font-size: 0.65rem; font-weight: 500; padding: 0.25rem 0.7rem; border-radius: 4px; }
.conf-h { background: var(--green-bg); color: var(--green); border: 1px solid var(--green-bdr); }
.conf-m { background: var(--amber-bg); color: var(--amber); border: 1px solid var(--amber-bdr); }
.conf-l { background: var(--red-bg);   color: var(--red);   border: 1px solid var(--red-bdr); }
.db-idea { font-size: 0.75rem; color: var(--muted); max-width: 240px; text-align: right; line-height: 1.4; }

/* ── Score cards ── */
.score-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.7rem; margin-bottom: 1rem; }
.score-card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--r);
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow);
}
.sc-label { font-family: var(--mono); font-size: 0.55rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.45rem; }
.sc-val   { font-size: 2rem; font-weight: 700; line-height: 1; letter-spacing: -0.03em; margin-bottom: 0.4rem; }
.scv-m { color: var(--accent); }
.scv-f { color: var(--green); }
.scv-r { color: var(--red); }
.sc-bar-wrap { height: 4px; background: var(--border); border-radius: 2px; margin-bottom: 0.45rem; overflow: hidden; }
.sc-bar { height: 100%; border-radius: 2px; }
.scb-m { background: var(--accent); }
.scb-f { background: var(--green); }
.scb-r { background: var(--red); }
.sc-sum { font-size: 0.75rem; color: var(--muted); line-height: 1.55; }

/* ── Validation panel ── */
.val-head {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.65rem 1.2rem;
    background: var(--surface2); border-bottom: 1px solid var(--border);
}
.val-title { font-family: var(--mono); font-size: 0.58rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
.vstat-ok   { font-family: var(--mono); font-size: 0.6rem; color: var(--green); background: var(--green-bg); padding: 0.15rem 0.5rem; border-radius: 3px; border: 1px solid var(--green-bdr); }
.vstat-fail { font-family: var(--mono); font-size: 0.6rem; color: var(--red);   background: var(--red-bg);   padding: 0.15rem 0.5rem; border-radius: 3px; border: 1px solid var(--red-bdr); }
.val-body { padding: 0.8rem 1.2rem; display: flex; flex-direction: column; gap: 0.35rem; }
.val-row { display: flex; align-items: center; gap: 0.6rem; font-family: var(--mono); font-size: 0.67rem; }
.vi-ok   { color: var(--green); }
.vi-fail { color: var(--red); }
.vi-warn { color: var(--amber); }
.vk { color: var(--muted); min-width: 150px; }
.vm { color: var(--text); }

/* ── Actions ── */
.actions-body { padding: 0.9rem 1.2rem; display: flex; flex-direction: column; gap: 0.5rem; }
.action-item { display: flex; align-items: flex-start; gap: 0.6rem; }
.a-num { font-family: var(--mono); font-size: 0.6rem; font-weight: 600; color: var(--accent); background: var(--accent-bg); border: 1px solid var(--accent-bdr); padding: 0.05rem 0.45rem; border-radius: 3px; min-width: 26px; text-align: center; margin-top: 2px; flex-shrink: 0; }
.a-txt { font-size: 0.85rem; color: var(--text); line-height: 1.55; }

/* ── JSON panel ── */
.json-body { padding: 1rem 1.2rem; font-family: var(--mono); font-size: 0.7rem; line-height: 1.9; color: #5a6a7a; white-space: pre-wrap; word-break: break-word; background: #f9f8f5; }
.jk  { color: var(--accent); }
.jvn { color: var(--amber); }
.jvs { color: var(--green); }
.jva { color: #7c3aed; }

/* ── Stats ── */
.stats-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.8rem 0 1.2rem; }
.stat { font-family: var(--mono); font-size: 0.59rem; color: var(--muted); background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 0.22rem 0.65rem; box-shadow: var(--shadow); }
.stat b { color: var(--text); }

/* ── Error ── */
.err-box { background: var(--red-bg); border: 1px solid var(--red-bdr); border-left: 3px solid var(--red); border-radius: var(--r); padding: 0.9rem 1.2rem; font-size: 0.82rem; color: var(--red); line-height: 1.6; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def dc(d): return "db-invest" if "invest" in d.lower() and "consider" not in d.lower() else ("db-consider" if "consider" in d.lower() else "db-reject")
def cc(c): return "conf-h" if c.lower()=="high" else ("conf-m" if c.lower() in ["medium","med"] else "conf-l")

def render_json_colored(data):
    lines = ["{"]
    items = list(data.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i < len(items)-1 else ""
        if isinstance(v, (int, float)):
            lines.append(f'  <span class="jk">"{k}"</span>: <span class="jvn">{v}</span>{comma}')
        elif isinstance(v, list):
            lines.append(f'  <span class="jk">"{k}"</span>: [')
            for j, item in enumerate(v):
                ic = "," if j < len(v)-1 else ""
                lines.append(f'    <span class="jva">"{item}"</span>{ic}')
            lines.append(f"  ]{comma}")
        else:
            lines.append(f'  <span class="jk">"{k}"</span>: <span class="jvs">"{v}"</span>{comma}')
    lines.append("}")
    return "\n".join(lines)

def render_log(lines, ph):
    rows = ""
    for t, tag, cls, msg in lines:
        rows += (f'<div class="el-line">'
                 f'<span class="el-t">{t}</span>'
                 f'<span class="el-tag {cls}">{tag}</span>'
                 f'<span class="el-msg">{msg}</span></div>')
    ph.markdown(f"""
    <div class="exec-log">
        <div class="el-head">
            <div class="el-dots">
                <div class="el-dot" style="background:#e06060"></div>
                <div class="el-dot" style="background:#f0a500"></div>
                <div class="el-dot" style="background:#7ec87e"></div>
            </div>
            <span class="el-title">Execution Log — Modular Pipeline</span>
        </div>
        <div class="el-body">{rows}</div>
    </div>""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hdr">
    <div>
        <div class="hdr-title">⬢ Modular Analyzer</div>
        <div class="hdr-sub">AgentForge · Day 10 · Clean Architecture + Separation of Concerns</div>
        <div class="hdr-tags">
            <span class="hdr-tag ht-blue">Modular Design</span>
            <span class="hdr-tag ht-green">6 Modules</span>
            <span class="hdr-tag ht-amber">5 Agents</span>
            <span class="hdr-tag ht-blue">Production Architecture</span>
        </div>
    </div>
    <div class="day-badge">DAY 10</div>
</div>
""", unsafe_allow_html=True)

# ── Architecture diagram ──────────────────────────────────────────────────────
st.markdown("""
<div class="arch-panel">
    <div class="arch-head">
        <span class="arch-title">Project Architecture — Module Dependency Graph</span>
        <span style="font-family:var(--mono);font-size:0.58rem;color:var(--green);">separation of concerns</span>
    </div>
    <div class="arch-body">
        <div class="dep-flow">
            <span class="dep-file">app.py</span>
            <span class="dep-arrow">→ imports →</span>
            <span class="dep-file">execution.py</span>
            <span class="dep-arrow">→ imports →</span>
            <span class="dep-file">crew_setup.py</span>
            <span class="dep-arrow">→ imports →</span>
            <span class="dep-file">agents.py</span>
            <span class="dep-arrow">+</span>
            <span class="dep-file">tasks.py</span>
            <span class="dep-arrow">+</span>
            <span class="dep-file">tools.py</span>
            <span class="dep-arrow">+</span>
            <span class="dep-file">utils.py</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Module cards ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="module-grid">
    <div class="module-card mc-tools">
        <div class="mc-filename">tools.py <span class="mc-badge mb-py">python</span></div>
        <div class="mc-desc">Custom tool definitions. Each tool is a BaseTool subclass with name, description, and _run(). Never imported by app.py directly.</div>
        <div class="mc-exports">
            <span class="mc-export">MarketSizeTool</span>
            <span class="mc-export">ROICalculatorTool</span>
            <span class="mc-export">CompetitorIntelTool</span>
            <span class="mc-export">get_research_tools()</span>
        </div>
    </div>
    <div class="module-card mc-agents">
        <div class="mc-filename">agents.py <span class="mc-badge mb-py">python</span></div>
        <div class="mc-desc">Agent definitions only. No task logic. Tools injected from tools.py. Each agent has role, goal, backstory — nothing else.</div>
        <div class="mc-exports">
            <span class="mc-export">create_manager()</span>
            <span class="mc-export">create_market_analyst()</span>
            <span class="mc-export">create_financial_analyst()</span>
            <span class="mc-export">create_all_agents()</span>
        </div>
    </div>
    <div class="module-card mc-tasks">
        <div class="mc-filename">tasks.py <span class="mc-badge mb-py">python</span></div>
        <div class="mc-desc">Task definitions and JSON schema. Schema lives here — single source of truth. Tasks receive agents as parameters.</div>
        <div class="mc-exports">
            <span class="mc-export">create_market_research_task()</span>
            <span class="mc-export">create_financial_task()</span>
            <span class="mc-export">create_main_evaluation_task()</span>
            <span class="mc-export">JSON_SCHEMA</span>
        </div>
    </div>
    <div class="module-card mc-crew">
        <div class="mc-filename">crew_setup.py <span class="mc-badge mb-core">core</span></div>
        <div class="mc-desc">Assembles agents + tasks into a crew. Returns Crew object — does not execute. Single integration point between modules.</div>
        <div class="mc-exports">
            <span class="mc-export">create_startup_crew()</span>
        </div>
    </div>
    <div class="module-card mc-utils">
        <div class="mc-filename">utils.py <span class="mc-badge mb-py">python</span></div>
        <div class="mc-desc">Shared utilities with no CrewAI imports. Input validation, JSON extraction, output validation, retry wrapper, cost estimator.</div>
        <div class="mc-exports">
            <span class="mc-export">validate_input()</span>
            <span class="mc-export">extract_json_safe()</span>
            <span class="mc-export">validate_output()</span>
            <span class="mc-export">safe_kickoff()</span>
        </div>
    </div>
    <div class="module-card mc-execution">
        <div class="mc-filename">execution.py <span class="mc-badge mb-core">core</span></div>
        <div class="mc-desc">The only module app.py imports. Orchestrates all layers: validate → build → kickoff → extract → validate output.</div>
        <div class="mc-exports">
            <span class="mc-export">run_startup_analysis()</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Presets ───────────────────────────────────────────────────────────────────
PRESETS = {
    "AI Logistics Optimizer": {
        "idea": (
            "An AI-powered logistics optimization SaaS for mid-size e-commerce companies shipping "
            "10,000–500,000 parcels/month. ML model reduces last-mile costs 15–25% through carrier "
            "optimization and delay prediction. Pricing: $2,000–$8,000/month. "
            "TAM: $75B growing at 14% CAGR. Moat: proprietary model trained on 50M+ shipments."
        ),
        "revenue": 480000, "cost": 160000, "industry": "Logistics AI",
    },
    "AI Legal Document Analyzer": {
        "idea": (
            "AI contract intelligence SaaS for solo lawyers billing $200–$500/hr. "
            "Scans contracts in 60 seconds, flags risky clauses, suggests redlines. "
            "Pricing: $149/month flat. TAM: $12B LegalTech at 26% CAGR. "
            "Risk: liability if AI misses a critical clause in a high-value contract."
        ),
        "revenue": 320000, "cost": 90000, "industry": "LegalTech AI",
    },
    "AI HR Screening Tool": {
        "idea": (
            "AI candidate screening SaaS for HR teams at companies hiring 50–500 employees/year. "
            "Auto-screens resumes, scores candidates, schedules interviews. "
            "Pricing: $500/month per active posting. TAM: $28B recruitment tech. "
            "Risk: AI hiring bias liability and EU/US regulations on automated hiring decisions."
        ),
        "revenue": 560000, "cost": 200000, "industry": "HR Tech AI",
    },
    "AI Crypto Trading Bot": {
        "idea": (
            "Retail-facing AI crypto trading bot executing algorithmic trades on technical signals "
            "and sentiment analysis. $99/month + 0.5% performance fee. TAM: $2.3B. "
            "Risks: regulatory uncertainty across jurisdictions, user loss liability, "
            "extreme volatility, and competition from established quant firms."
        ),
        "revenue": 180000, "cost": 120000, "industry": "FinTech AI",
    },
    "Custom Startup Idea": {"idea": "", "revenue": 500000, "cost": 150000, "industry": "AI SaaS"},
}

MODELS = {
    "Gemini (Recommended)": {
        "gemini/gemini-2.5-flash": "Gemini 2.5 Flash  ✓ Free",
        "gemini/gemini-2.0-flash": "Gemini 2.0 Flash",
    },
    "Groq (Fallback)": {
        "groq/llama-3.3-70b-versatile": "LLaMA 3.3 70B",
        "groq/mixtral-8x7b-32768":      "Mixtral 8x7B",
    },
}

# ── Form ──────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    st.markdown('<span class="slabel">Startup Preset</span>', unsafe_allow_html=True)
    preset = st.selectbox("preset", list(PRESETS.keys()), label_visibility="collapsed")
with col2:
    st.markdown('<span class="slabel">Provider</span>', unsafe_allow_html=True)
    prov = st.selectbox("prov", list(MODELS.keys()), label_visibility="collapsed")
with col3:
    st.markdown('<span class="slabel">Model</span>', unsafe_allow_html=True)
    model_opts = MODELS[prov]
    model_id = st.selectbox("mod", list(model_opts.keys()),
                             format_func=lambda x: model_opts[x], label_visibility="collapsed")

p = PRESETS[preset]
is_gemini = model_id.startswith("gemini/")

st.markdown('<span class="slabel">Startup Description</span>', unsafe_allow_html=True)
startup_idea = st.text_area("idea", value=p["idea"], height=100,
    placeholder="Describe the startup with market size, pricing model, moat, and key risks...",
    label_visibility="collapsed")

st.markdown('<span class="slabel">ROI Inputs</span>', unsafe_allow_html=True)
col_r, col_c, col_i = st.columns(3)
with col_r:
    revenue = st.number_input("Annual Revenue ($)", value=float(p["revenue"]),
                               min_value=0.0, step=10000.0, format="%.0f")
with col_c:
    cost = st.number_input("Annual Cost ($)", value=float(p["cost"]),
                            min_value=0.0, step=10000.0, format="%.0f")
with col_i:
    INDUSTRIES = ["AI SaaS", "Logistics AI", "LegalTech AI", "HR Tech AI", "FinTech AI",
                  "Real Estate AI", "AI Marketing", "EdTech AI", "HealthTech AI"]
    default_i = INDUSTRIES.index(p["industry"]) if p["industry"] in INDUSTRIES else 0
    industry = st.selectbox("Industry", INDUSTRIES, index=default_i, label_visibility="visible")

with st.expander("⚙  Advanced — Architecture + Analysis Settings"):
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        use_specialists = st.toggle(
            "5-Agent Specialist Mode",
            value=True,
            help="ON = 5 agents (market + financial + risk + advisor + manager). OFF = 1 agent direct."
        )
        persona = st.selectbox("Analyst Persona",
            ["Venture Capital Partner", "Angel Investor",
             "Private Equity Analyst", "Startup Accelerator"])
    with col_a2:
        stage = st.selectbox("Investment Stage",
            ["Pre-seed", "Seed", "Series A", "Series B+"])
        risk_tolerance = st.selectbox("Risk Tolerance",
            ["Conservative", "Balanced", "Aggressive"])
    max_retries = st.slider("Max Retries", 1, 5, 3)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1,
                             help="Lower = more stable JSON. Recommended 0.1–0.3 for structured output.")

st.markdown('<div class="div"></div>', unsafe_allow_html=True)
run_btn = st.button("⬢  RUN MODULAR ANALYSIS PIPELINE")


# ── Execution ──────────────────────────────────────────────────────────────────
if run_btn:
    api_key = os.environ.get("GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY", "")
    if not api_key:
        st.markdown(f'<div class="err-box">⚠ {"GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY"} not found in Streamlit Secrets.</div>', unsafe_allow_html=True)
        st.stop()

    try:
        from execution import run_startup_analysis
    except ImportError:
        st.markdown('<div class="err-box">⚠ Could not import execution.py — make sure all module files are in the same directory as app.py.</div>', unsafe_allow_html=True)
        st.stop()

    t0       = time.time()
    log_ph   = st.empty()
    status_ph = st.empty()
    log      = []
    ts       = lambda: f"{round(time.time()-t0,1):>5}s"

    # Live import log — shows each module being called
    mode_label = "5-agent specialist" if use_specialists else "1-agent direct"
    log.append((ts(), "MOD", "lt-mod", "app.py → importing execution.py"))
    render_log(log, log_ph); time.sleep(0.2)
    log.append((ts(), "MOD", "lt-mod", "execution.py → crew_setup.py + utils.py"))
    render_log(log, log_ph); time.sleep(0.2)
    log.append((ts(), "MOD", "lt-mod", "crew_setup.py → agents.py + tasks.py + tools.py"))
    render_log(log, log_ph); time.sleep(0.2)
    log.append((ts(), "SYS", "lt-sys",
                f"Pipeline: validate → crew_setup → kickoff → extract → validate | mode: {mode_label}"))
    render_log(log, log_ph)

    status_ph.markdown("""
    <div class="status-bar">
        <div class="s-dot s-run"></div>
        <span class="s-text">Modular pipeline executing…</span>
    </div>""", unsafe_allow_html=True)

    result = run_startup_analysis(
        startup_idea    = startup_idea,
        model_id        = model_id,
        api_key         = api_key,
        revenue         = revenue,
        cost            = cost,
        industry        = industry,
        persona         = persona if 'persona' in dir() else "Venture Capital Partner",
        stage           = stage if 'stage' in dir() else "Seed",
        risk_tolerance  = risk_tolerance if 'risk_tolerance' in dir() else "Balanced",
        temperature     = temperature if 'temperature' in dir() else 0.2,
        use_specialists = use_specialists,
        max_retries     = max_retries if 'max_retries' in dir() else 3,
        auto_regen      = True,
    )

    elapsed = round(time.time() - t0, 1)

    # Log the outcome
    log.append((ts(), "SYS", "lt-sys", f"Stage returned: {result.get('stage','unknown')} · {elapsed}s"))
    if result["success"]:
        log.append((ts(), "JSON", "lt-json", "JSON extracted ✓"))
        val = result.get("validation", [])
        passed = sum(1 for r in val if r[3])
        log.append((ts(), "VAL", "lt-val",
                    f"Validation: {passed}/{len(val)} checks passed"))
    else:
        log.append((ts(), "ERR", "lt-err",
                    f"Pipeline failed at: {result.get('stage','unknown')} — {str(result.get('error',''))[:80]}"))
    render_log(log, log_ph)

    # Status bar
    if result["success"]:
        all_ok = result.get("all_passed", False)
        status_ph.markdown(f"""
        <div class="status-bar">
            <div class="s-dot s-ok"></div>
            <span class="s-text">Pipeline complete — {result['attempts']} attempt(s) · {'All checks passed' if all_ok else 'Review validation'}</span>
            <span class="s-meta">{elapsed}s</span>
        </div>""", unsafe_allow_html=True)
    else:
        status_ph.markdown(f"""
        <div class="status-bar">
            <div class="s-dot s-err"></div>
            <span class="s-text">Pipeline failed at {result.get('stage','unknown')}</span>
            <span class="s-meta">{elapsed}s</span>
        </div>""", unsafe_allow_html=True)

    if not result["success"]:
        err_str = str(result.get("error", "Unknown error"))
        if "quota" in err_str.lower() or "429" in err_str or "resource_exhausted" in err_str.lower():
            st.markdown('<div class="err-box"><b>Quota Exhausted (429)</b><br>Switch to Gemini 2.5 Flash and wait 60 seconds.</div>', unsafe_allow_html=True)
        elif "rate_limit" in err_str.lower():
            st.markdown('<div class="err-box"><b>Rate limit hit.</b> Wait 30–60s and retry.</div>', unsafe_allow_html=True)
        elif result.get("stage") == "input_validation":
            st.markdown(f'<div class="err-box"><b>Input validation failed:</b> {err_str}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="err-box"><b>Error ({result.get("stage","")}):</b> {err_str}</div>', unsafe_allow_html=True)
        st.stop()

    parsed = result["data"]
    val    = result["validation"]
    all_ok = result.get("all_passed", False)

    decision   = str(parsed.get("final_decision", "Unknown")).strip()
    confidence = str(parsed.get("confidence_level", "Low")).strip()
    ms  = parsed.get("market_score", 0)
    fs  = parsed.get("financial_score", 0)
    rs  = parsed.get("risk_score", 0)
    tot = parsed.get("total_score", round((ms + fs + (10 - rs)) / 3, 1))

    # Decision banner
    db_cls = dc(decision); cf_cls = cc(confidence)
    idea_short = startup_idea[:80] + "…" if len(startup_idea) > 80 else startup_idea
    st.markdown(f"""
    <div class="decision-banner {db_cls}">
        <div>
            <div class="db-label">Final Decision</div>
            <div class="db-dec">{decision}</div>
        </div>
        <div class="db-right">
            <span class="db-conf {cf_cls}">Confidence: {confidence}</span>
            <span class="db-idea">{idea_short}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # Score grid
    st.markdown(f"""
    <div class="score-grid">
        <div class="score-card">
            <div class="sc-label">Market Score</div>
            <div class="sc-val scv-m">{ms}<span style="font-size:0.85rem;color:var(--muted2)">/10</span></div>
            <div class="sc-bar-wrap"><div class="sc-bar scb-m" style="width:{ms*10}%"></div></div>
            <div class="sc-sum">{str(parsed.get("market_summary",""))[:160]}</div>
        </div>
        <div class="score-card">
            <div class="sc-label">Financial Score</div>
            <div class="sc-val scv-f">{fs}<span style="font-size:0.85rem;color:var(--muted2)">/10</span></div>
            <div class="sc-bar-wrap"><div class="sc-bar scb-f" style="width:{fs*10}%"></div></div>
            <div class="sc-sum">{str(parsed.get("financial_summary",""))[:160]}</div>
        </div>
        <div class="score-card">
            <div class="sc-label">Risk Score</div>
            <div class="sc-val scv-r">{rs}<span style="font-size:0.85rem;color:var(--muted2)">/10</span></div>
            <div class="sc-bar-wrap"><div class="sc-bar scb-r" style="width:{rs*10}%"></div></div>
            <div class="sc-sum">{str(parsed.get("risk_summary",""))[:160]}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Validation
    fail_c = sum(1 for r in val if not r[3])
    vstat  = (f'<span class="vstat-ok">ALL {len(val)} CHECKS PASSED</span>'
              if all_ok else f'<span class="vstat-fail">{fail_c} ISSUE(S)</span>')
    val_rows = ""
    for icon, key, msg, passed in val:
        ic = "vi-ok" if icon=="✓" else ("vi-warn" if icon=="⚠" else "vi-fail")
        val_rows += f'<div class="val-row"><span class="{ic}">{icon}</span><span class="vk">{key}</span><span class="vm">— {msg}</span></div>'
    st.markdown(f"""
    <div class="result-section">
        <div class="val-head"><span class="val-title">Validation Pipeline</span>{vstat}</div>
        <div class="val-body">{val_rows}</div>
    </div>""", unsafe_allow_html=True)

    # Actions
    actions = parsed.get("recommended_actions", [])
    if isinstance(actions, list) and actions:
        items = "".join([f'<div class="action-item"><span class="a-num">{i:02d}</span><span class="a-txt">{a}</span></div>'
                         for i, a in enumerate(actions[:7], 1)])
        st.markdown(f"""
        <div class="result-section">
            <div class="rs-head"><span class="rs-badge rb-blue">Recommended Actions</span></div>
            <div class="actions-body">{items}</div>
        </div>""", unsafe_allow_html=True)

    # Stats
    cost_est = result.get("cost_estimate", {})
    agents_label = "5 specialists" if use_specialists else "1 direct"
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat">total score <b>{tot}/10</b></div>
        <div class="stat">decision <b>{decision}</b></div>
        <div class="stat">agents <b>{agents_label}</b></div>
        <div class="stat">attempts <b>{result['attempts']}</b></div>
        <div class="stat">est. tokens <b>{cost_est.get('total_tokens','—')}</b></div>
        <div class="stat">elapsed <b>{elapsed}s</b></div>
        <div class="stat">model <b>{model_id.split('/')[1]}</b></div>
    </div>""", unsafe_allow_html=True)

    # Raw JSON
    st.markdown(f"""
    <div class="result-section">
        <div class="rs-head">
            <span class="rs-badge rb-green">Raw JSON Output</span>
            <span style="font-family:var(--mono);font-size:0.58rem;color:var(--green);">db-ready · validated</span>
        </div>
        <div class="json-body">{render_json_colored(parsed)}</div>
    </div>""", unsafe_allow_html=True)
