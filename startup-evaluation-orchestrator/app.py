import streamlit as st
import os
import time
import json
import re
import logging
import io
from datetime import datetime

st.set_page_config(
    page_title="Startup Evaluation · Orchestrator",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Secrets ──────────────────────────────────────────────────────────────────────
for k in ["GEMINI_API_KEY", "GROQ_API_KEY"]:
    try:
        os.environ[k] = st.secrets[k]
    except Exception:
        pass
os.environ.setdefault("OPENAI_API_KEY", "dummy-not-used")

# ── Session-state monitoring counters ────────────────────────────────────────────
for key, default in [
    ("total_requests", 0),
    ("failed_requests", 0),
    ("total_time", 0.0),
    ("run_log", []),        # list of log entries [{ts, level, msg}]
    ("run_history", []),    # list of completed runs [{name, decision, time, status}]
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── In-memory log handler ─────────────────────────────────────────────────────────
class SessionLogHandler(logging.Handler):
    def emit(self, record):
        level = record.levelname
        msg   = self.format(record)
        st.session_state["run_log"].append({
            "ts":    datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "level": level,
            "msg":   msg,
        })

logger = logging.getLogger("agentforge.day11")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = SessionLogHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s · %(message)s"))
    logger.addHandler(handler)

def log_event(msg, level="INFO"):
    getattr(logger, level.lower(), logger.info)(msg)

# ══════════════════════════════════════════════════════════════════════════════════
# CSS — Observability Terminal Aesthetic
# Inspired by: Datadog, Grafana, Honeycomb
# Color: Deep terminal green on near-black · Amber alerts · Red errors
# Type: Fragment Mono + IBM Plex Sans
# ══════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fragment+Mono:ital@0;1&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --bg:          #080c08;
    --bg2:         #0b100b;
    --surface:     #0d120d;
    --surface2:    #111811;
    --surface3:    #161e16;
    --border:      rgba(74,222,128,0.10);
    --border2:     rgba(74,222,128,0.20);
    --border3:     rgba(74,222,128,0.35);

    --green:       #4ade80;
    --green-dim:   rgba(74,222,128,0.10);
    --green-glow:  rgba(74,222,128,0.15);
    --green-dark:  #16a34a;
    --green-text:  #86efac;

    --amber:       #fbbf24;
    --amber-dim:   rgba(251,191,36,0.10);
    --amber-bd:    rgba(251,191,36,0.25);

    --red:         #f87171;
    --red-dim:     rgba(248,113,113,0.10);
    --red-bd:      rgba(248,113,113,0.25);

    --blue:        #60a5fa;
    --blue-dim:    rgba(96,165,250,0.10);
    --blue-bd:     rgba(96,165,250,0.25);

    --cyan:        #22d3ee;
    --cyan-dim:    rgba(34,211,238,0.08);

    --text:        #d4e8d4;
    --text2:       #8aaa8a;
    --text3:       #4a664a;
    --text4:       #2a3a2a;

    --mono:        'Fragment Mono', 'IBM Plex Mono', monospace;
    --sans:        'IBM Plex Sans', sans-serif;

    --r:           6px;
    --r-lg:        10px;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: var(--sans) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    -webkit-font-smoothing: antialiased;
}

/* Scanline texture overlay */
body::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
    );
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 1.5rem 6rem !important;
    max-width: 980px !important;
    position: relative; z-index: 1;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ── HEADER ── */
.obs-header {
    background: var(--surface);
    border-bottom: 1px solid var(--border2);
    padding: 1.5rem 2rem 1.25rem;
    margin: 0 -1.5rem 2rem;
    position: relative; overflow: hidden;
}
.obs-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--green), var(--cyan), transparent);
}
/* Subtle grid */
.obs-header::after {
    content: '';
    position: absolute; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(74,222,128,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(74,222,128,0.03) 1px, transparent 1px);
    background-size: 32px 32px;
}
.obs-header-inner { position: relative; z-index: 1; }
.obs-eyebrow {
    display: inline-flex; align-items: center; gap: 0.5rem;
    font-family: var(--mono); font-size: 0.65rem; font-weight: 500;
    color: var(--green); letter-spacing: 0.14em; text-transform: uppercase;
    border: 1px solid var(--border2); border-radius: 3px;
    padding: 0.25rem 0.65rem; margin-bottom: 0.8rem;
    background: var(--green-dim);
}
.pulse {
    width: 6px; height: 6px; border-radius: 50%; background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.8)} }

.obs-title {
    font-family: var(--mono); font-size: 2rem; font-weight: normal;
    color: var(--green-text); letter-spacing: -0.02em;
    margin-bottom: 0.4rem; line-height: 1.1;
}
.obs-title span { color: var(--green); }
.obs-sub {
    font-size: 0.88rem; color: var(--text2); line-height: 1.6;
    max-width: 520px; font-weight: 300;
}
.obs-meta {
    display: flex; align-items: center; gap: 1.5rem;
    margin-top: 1.1rem; flex-wrap: wrap;
}
.obs-meta-item {
    font-family: var(--mono); font-size: 0.65rem; color: var(--text3);
    display: flex; align-items: center; gap: 0.4rem; letter-spacing: 0.06em;
}
.obs-meta-dot { width: 4px; height: 4px; border-radius: 50%; background: var(--green); }
.obs-day-badge {
    margin-left: auto; font-family: var(--mono); font-size: 0.65rem;
    color: var(--text3); background: var(--surface2);
    border: 1px solid var(--border); padding: 0.3rem 0.7rem; border-radius: var(--r);
    letter-spacing: 0.08em;
}

/* ── METRIC CARDS ── */
.metrics-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem; margin-bottom: 1.75rem;
}
.metric-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r-lg); padding: 1.1rem 1rem;
    position: relative; overflow: hidden;
    transition: border-color 0.2s ease;
}
.metric-card:hover { border-color: var(--border2); }
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.mc-green::before  { background: var(--green); }
.mc-amber::before  { background: var(--amber); }
.mc-red::before    { background: var(--red); }
.mc-blue::before   { background: var(--blue); }

.metric-val {
    font-family: var(--mono); font-size: 2rem; font-weight: 500;
    line-height: 1; margin-bottom: 0.3rem; letter-spacing: -0.03em;
}
.mc-green .metric-val { color: var(--green); }
.mc-amber .metric-val { color: var(--amber); }
.mc-red   .metric-val { color: var(--red);   }
.mc-blue  .metric-val { color: var(--blue);  }

.metric-label {
    font-family: var(--mono); font-size: 0.6rem; color: var(--text3);
    letter-spacing: 0.1em; text-transform: uppercase;
}
.metric-sub {
    font-family: var(--mono); font-size: 0.62rem; color: var(--text3);
    margin-top: 0.15rem;
}

/* ── SECTION LABEL ── */
.sec-label {
    font-family: var(--mono); font-size: 0.62rem; color: var(--text3);
    letter-spacing: 0.14em; text-transform: uppercase;
    display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;
}
.sec-label::before {
    content: ''; display: block; width: 12px; height: 1px; background: var(--green);
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
    caret-color: var(--green) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px var(--green-dim) !important;
}
.stTextArea > div > div > textarea::placeholder,
.stTextInput > div > div > input::placeholder {
    color: var(--text3) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-family: var(--mono) !important;
    font-size: 0.64rem !important;
    color: var(--text3) !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* ── BUTTON ── */
.stButton > button {
    width: 100% !important;
    background: var(--green-dim) !important;
    color: var(--green) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r) !important;
    padding: 0.85rem 2rem !important;
    font-family: var(--mono) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.08em !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: rgba(74,222,128,0.18) !important;
    border-color: var(--border3) !important;
    box-shadow: 0 0 20px var(--green-glow) !important;
    transform: translateY(-1px) !important;
}

/* ── DIVIDER ── */
.div {
    height: 1px; background: var(--border); margin: 1.5rem 0;
}
.div-green {
    height: 1px;
    background: linear-gradient(90deg, var(--border2), transparent);
    margin: 1.5rem 0;
}

/* ── TRACE LOG ── */
.trace-shell {
    background: var(--bg); border: 1px solid var(--border2);
    border-radius: var(--r-lg); overflow: hidden;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 var(--border);
}
.trace-titlebar {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.7rem 1rem;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
}
.trace-dot { width: 8px; height: 8px; border-radius: 50%; }
.td-r { background: #f87171; opacity: 0.7; }
.td-y { background: #fbbf24; opacity: 0.7; }
.td-g { background: #4ade80; opacity: 0.7; animation: pulse 2s infinite; }
.trace-title {
    font-family: var(--mono); font-size: 0.65rem; color: var(--text3);
    letter-spacing: 0.1em; margin-left: 0.3rem;
}
.trace-body {
    padding: 0.75rem 1rem; max-height: 280px; overflow-y: auto;
    font-family: var(--mono); font-size: 0.72rem;
}
.trace-line {
    display: flex; align-items: baseline; gap: 0.75rem;
    padding: 0.18rem 0; border-bottom: 1px solid rgba(74,222,128,0.04);
    line-height: 1.4;
}
.trace-ts  { color: var(--text4); min-width: 72px; font-size: 0.66rem; flex-shrink: 0; }
.trace-lvl {
    font-size: 0.6rem; font-weight: 600; padding: 0.1rem 0.45rem;
    border-radius: 3px; letter-spacing: 0.06em; min-width: 48px;
    text-align: center; flex-shrink: 0;
}
.lvl-info  { background: var(--green-dim);  color: var(--green);  border: 1px solid var(--border2); }
.lvl-warn  { background: var(--amber-dim);  color: var(--amber);  border: 1px solid var(--amber-bd); }
.lvl-error { background: var(--red-dim);    color: var(--red);    border: 1px solid var(--red-bd); }
.lvl-debug { background: var(--blue-dim);   color: var(--blue);   border: 1px solid var(--blue-bd); }
.trace-msg { color: var(--text2); }

/* ── TIMELINE ── */
.timeline-shell {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r-lg); overflow: hidden; margin-bottom: 1.5rem;
}
.timeline-header {
    padding: 0.75rem 1.1rem; border-bottom: 1px solid var(--border);
    background: var(--surface2);
    font-family: var(--mono); font-size: 0.65rem; color: var(--text3);
    letter-spacing: 0.1em; text-transform: uppercase;
}
.timeline-body { padding: 1rem 1.1rem; }
.tl-row {
    display: flex; align-items: center; gap: 0.75rem;
    margin-bottom: 0.6rem;
}
.tl-agent {
    font-family: var(--mono); font-size: 0.65rem; color: var(--text2);
    min-width: 130px; flex-shrink: 0; letter-spacing: 0.03em;
}
.tl-bar-track {
    flex: 1; height: 20px; background: var(--surface2);
    border-radius: 3px; overflow: hidden; position: relative;
}
.tl-bar-fill {
    height: 100%; border-radius: 3px;
    display: flex; align-items: center; padding-left: 0.5rem;
    font-family: var(--mono); font-size: 0.58rem; color: var(--bg);
    font-weight: 600; white-space: nowrap;
    transition: width 1s cubic-bezier(0.4,0,0.2,1);
}
.tl-time {
    font-family: var(--mono); font-size: 0.62rem; color: var(--text3);
    min-width: 44px; text-align: right;
}

/* ── VERDICT / OUTPUT ── */
.verdict-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r-lg); overflow: hidden; margin-bottom: 1rem;
    position: relative;
}
.verdict-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--green), var(--cyan), transparent);
}
.verdict-header {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.85rem 1.2rem; background: var(--surface2);
    border-bottom: 1px solid var(--border);
}
.verdict-icon {
    width: 30px; height: 30px; border-radius: var(--r);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; flex-shrink: 0;
}
.vi-green { background: var(--green-dim); border: 1px solid var(--border2); }
.vi-amber { background: var(--amber-dim); border: 1px solid var(--amber-bd); }
.vi-red   { background: var(--red-dim);   border: 1px solid var(--red-bd);   }

.verdict-title {
    font-family: var(--mono); font-size: 0.8rem; color: var(--text);
    letter-spacing: 0.02em;
}
.verdict-agent {
    margin-left: auto; font-family: var(--mono); font-size: 0.6rem;
    color: var(--text3); background: var(--surface3);
    border: 1px solid var(--border); padding: 0.2rem 0.5rem; border-radius: 3px;
}
.verdict-body {
    padding: 1.2rem 1.3rem; font-size: 0.87rem; color: var(--text2); line-height: 1.75;
}
.verdict-body strong, .verdict-body b { color: var(--text); font-weight: 600; }
.verdict-body h1,.verdict-body h2,.verdict-body h3 {
    font-family: var(--mono); color: var(--green-text);
    font-size: 0.85rem; font-weight: 500; margin: 0.9rem 0 0.3rem;
    letter-spacing: 0.04em; text-transform: uppercase;
}

/* ── SCORE GRID ── */
.score-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 0.6rem; margin-bottom: 1.2rem;
}
.score-cell {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: var(--r); padding: 0.85rem 0.75rem; text-align: center;
    position: relative; overflow: hidden;
}
.score-cell::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
}
.sc-g::after { background: var(--green); }
.sc-b::after { background: var(--blue);  }
.sc-r::after { background: var(--red);   }
.sc-a::after { background: var(--amber); }

.score-num {
    font-family: var(--mono); font-size: 1.8rem; font-weight: 500;
    line-height: 1; letter-spacing: -0.04em;
}
.sc-g .score-num { color: var(--green); }
.sc-b .score-num { color: var(--blue);  }
.sc-r .score-num { color: var(--red);   }
.sc-a .score-num { color: var(--amber); }
.score-lbl {
    font-family: var(--mono); font-size: 0.58rem; color: var(--text3);
    letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.2rem;
}

/* ── DECISION CHIP ── */
.decision-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; }
.decision-chip {
    font-family: var(--mono); font-size: 0.82rem; font-weight: 600;
    padding: 0.45rem 1.1rem; border-radius: 3px; letter-spacing: 0.06em;
}
.chip-invest { background: var(--green-dim); color: var(--green); border: 1px solid var(--border2); }
.chip-cond   { background: var(--amber-dim); color: var(--amber); border: 1px solid var(--amber-bd); }
.chip-watch  { background: var(--blue-dim);  color: var(--blue);  border: 1px solid var(--blue-bd); }
.chip-pass   { background: var(--red-dim);   color: var(--red);   border: 1px solid var(--red-bd); }
.confidence-tag {
    font-family: var(--mono); font-size: 0.65rem; color: var(--text3);
    background: var(--surface3); border: 1px solid var(--border);
    padding: 0.3rem 0.6rem; border-radius: 3px; letter-spacing: 0.06em;
}

/* ── REASONING BOX ── */
.reasoning-box {
    background: var(--surface2); border: 1px solid var(--border);
    border-left: 3px solid var(--green); border-radius: var(--r);
    padding: 0.85rem 1rem; margin-bottom: 1rem;
    font-family: var(--mono); font-size: 0.78rem; color: var(--text2);
    line-height: 1.6;
}
.reasoning-label {
    font-size: 0.58rem; color: var(--green); letter-spacing: 0.12em;
    text-transform: uppercase; margin-bottom: 0.35rem; display: block;
}

/* ── JSON PANEL ── */
.json-shell {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: var(--r-lg); overflow: hidden; margin-top: 1rem;
}
.json-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 1rem; background: var(--surface);
    border-bottom: 1px solid var(--border);
    font-family: var(--mono); font-size: 0.63rem;
}
.json-bar-title { color: var(--text3); letter-spacing: 0.1em; }
.json-valid {
    color: var(--green); background: var(--green-dim);
    border: 1px solid var(--border2); padding: 0.15rem 0.5rem;
    border-radius: 3px; font-size: 0.6rem; letter-spacing: 0.06em;
}
.json-body { padding: 1rem; overflow-x: auto; }
.json-body pre {
    font-family: var(--mono); font-size: 0.75rem;
    color: var(--green-text); margin: 0; white-space: pre-wrap;
    word-break: break-word; line-height: 1.65;
}

/* ── FAILURE SIMULATION ── */
.fail-box {
    background: var(--red-dim); border: 1px solid var(--red-bd);
    border-left: 3px solid var(--red); border-radius: var(--r);
    padding: 0.9rem 1.1rem; margin-top: 1rem;
    font-family: var(--mono); font-size: 0.75rem; color: var(--red);
    line-height: 1.6;
}
.fail-box-title { font-weight: 600; margin-bottom: 0.3rem; font-size: 0.78rem; }

/* ── RUN HISTORY ── */
.history-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.6rem 0.9rem;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); margin-bottom: 0.4rem;
    font-family: var(--mono); font-size: 0.68rem;
}
.hist-num  { color: var(--text3); min-width: 28px; }
.hist-name { color: var(--text); flex: 1; }
.hist-dec  { min-width: 80px; text-align: center;
             padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.62rem; }
.hist-time { color: var(--text3); min-width: 48px; text-align: right; }
.hist-ok  { background: var(--green-dim); color: var(--green); border: 1px solid var(--border2); }
.hist-warn{ background: var(--amber-dim); color: var(--amber); border: 1px solid var(--amber-bd); }
.hist-err { background: var(--red-dim);   color: var(--red);   border: 1px solid var(--red-bd); }

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    color: var(--text2) !important;
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em !important;
}
.streamlit-expanderHeader:hover { border-color: var(--border2) !important; }
.streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r) var(--r) !important;
}
.stCheckbox label p { color: var(--text2) !important; font-size: 0.82rem !important; }

/* Footer */
.obs-footer {
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 1rem; border-top: 1px solid var(--border);
    font-family: var(--mono); font-size: 0.62rem; color: var(--text4);
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════════
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div class="obs-header">
  <div class="obs-header-inner">
    <div class="obs-eyebrow"><span class="pulse"></span>SYSTEM LIVE</div>
    <div class="obs-title">AgentForge <span>Observability</span></div>
    <div class="obs-sub">
      Logging · Monitoring · Tracing · Decision Explainability.
      Every agent action recorded. Every decision reasoned. Every failure tracked.
    </div>
    <div class="obs-meta">
      <span class="obs-meta-item"><span class="obs-meta-dot"></span>Structured JSON Logging</span>
      <span class="obs-meta-item"><span class="obs-meta-dot"></span>Execution Timing</span>
      <span class="obs-meta-item"><span class="obs-meta-dot"></span>Failure Counter</span>
      <span class="obs-meta-item"><span class="obs-meta-dot"></span>Decision Reasoning</span>
      <span class="obs-day-badge">DAY 11 · AGENT-FORGE</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# LIVE METRICS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════════
total  = st.session_state["total_requests"]
failed = st.session_state["failed_requests"]
passed = total - failed
avg_t  = round(st.session_state["total_time"] / total, 1) if total > 0 else 0.0
fail_r = round((failed / total) * 100, 1) if total > 0 else 0.0

st.markdown('<div class="sec-label">Live Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="metrics-grid">
  <div class="metric-card mc-green">
    <div class="metric-val">{total}</div>
    <div class="metric-label">Total Runs</div>
    <div class="metric-sub">{passed} successful</div>
  </div>
  <div class="metric-card mc-red">
    <div class="metric-val">{failed}</div>
    <div class="metric-label">Failed Runs</div>
    <div class="metric-sub">{fail_r}% failure rate</div>
  </div>
  <div class="metric-card mc-amber">
    <div class="metric-val">{avg_t}s</div>
    <div class="metric-label">Avg Exec Time</div>
    <div class="metric-sub">per crew run</div>
  </div>
  <div class="metric-card mc-blue">
    <div class="metric-val">{len(st.session_state["run_log"])}</div>
    <div class="metric-label">Log Events</div>
    <div class="metric-sub">this session</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# RUN HISTORY TABLE
# ══════════════════════════════════════════════════════════════════════════════════
if st.session_state["run_history"]:
    st.markdown('<div class="sec-label">Run History</div>', unsafe_allow_html=True)
    dec_cls = {"INVEST":"hist-ok","CONDITIONAL":"hist-warn","WATCH":"hist-warn","PASS":"hist-err","ERROR":"hist-err"}
    for i, r in enumerate(reversed(st.session_state["run_history"][-8:]), 1):
        cls = dec_cls.get(r.get("decision","ERROR"), "hist-err")
        st.markdown(f"""
        <div class="history-row">
          <span class="hist-num">#{total - i + 1}</span>
          <span class="hist-name">{r['name'][:42]}</span>
          <span class="hist-dec {cls}">{r.get('decision','ERROR')}</span>
          <span class="hist-time">{r['time']}s</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# INPUT FORM
# ══════════════════════════════════════════════════════════════════════════════════
PRESETS = {
    "AI Medical Booking Platform": "An AI-powered medical appointment platform that matches patients with specialist doctors using symptom-based ML. Currently has 12 partner clinics, 800 monthly bookings, 3-month waitlist from 6 more hospitals. Revenue: 8% commission per appointment + $299/month SaaS. Target: 500 clinics in Southeast Asia by 2027.",
    "AI Logistics Optimizer":      "An AI logistics platform for last-mile delivery using real-time traffic and dynamic routing. Reduces delivery costs 30–35%. Clients: Pathao, Paperfly. ARR: $180K. Growing 22% MoM. Raising $1.2M Series A.",
    "AI Legal Document Analyzer":  "AI contract review for law firms — flags risky clauses, extracts obligations, compares to standard templates. Reduces review time 70%. B2B SaaS $299/month. No traction yet. Three founders, no legal background.",
    "AI Farming Automation":       "Precision agriculture platform with satellite imagery + IoT sensors. Targets 100+ acre commercial farms in South Asia. Pre-seed, no revenue, strong academic team from BUET.",
    "INTENTIONAL FAILURE TEST":    "",  # empty — triggers failure counter
}

st.markdown('<div class="sec-label">Startup Analysis Input</div>', unsafe_allow_html=True)
col_pre, col_mod = st.columns([3, 2])
with col_pre:
    preset_choice = st.selectbox("STARTUP PRESET", list(PRESETS.keys()))
with col_mod:
    model_id = st.selectbox("MODEL", [
        "gemini/gemini-2.5-flash",
        "groq/llama-3.3-70b-versatile",
        "groq/mixtral-8x7b-32768",
    ], format_func=lambda x: x.split("/")[1])

is_gemini = model_id.startswith("gemini/")

startup_idea = st.text_area(
    "STARTUP DESCRIPTION",
    value=st.session_state.get("idea_text", PRESETS[preset_choice]),
    height=110,
    placeholder="Describe the startup in detail for analysis...",
)

col_n, col_s = st.columns(2)
with col_n:
    startup_name = st.text_input("STARTUP NAME", value=preset_choice if preset_choice != "INTENTIONAL FAILURE TEST" else "")
with col_s:
    stage = st.selectbox("FUNDING STAGE", ["Concept Only", "Pre-Seed", "Seed", "Series A", "Series B+"])

with st.expander("⚙  OBSERVABILITY SETTINGS"):
    col_a, col_b = st.columns(2)
    with col_a:
        log_level    = st.selectbox("LOG LEVEL", ["INFO", "DEBUG", "WARNING"])
        depth        = st.select_slider("ANALYSIS DEPTH", ["Brief","Standard","Detailed"], value="Standard")
    with col_b:
        investor_type = st.selectbox("INVESTOR LENS",
            ["Venture Capital","Angel Investor","Private Equity","Impact Investor"])
        geography    = st.selectbox("GEOGRAPHY",
            ["Global","Southeast Asia","South Asia","USA & Canada","Europe"])
    col_c, col_d, col_e = st.columns(3)
    with col_c: show_trace    = st.checkbox("Show trace log",    value=True)
    with col_d: show_timeline = st.checkbox("Show timeline",     value=True)
    with col_e: show_json     = st.checkbox("Show JSON verdict", value=True)

st.markdown('<div class="div"></div>', unsafe_allow_html=True)
run_btn   = st.button("◈  DEPLOY AGENTS + START TRACE")
reset_btn = st.button("↺  RESET METRICS")

if reset_btn:
    for k in ["total_requests","failed_requests","total_time","run_log","run_history"]:
        st.session_state[k] = 0 if k in ["total_requests","failed_requests"] else (0.0 if k == "total_time" else [])
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════════
# EXECUTION
# ══════════════════════════════════════════════════════════════════════════════════
if run_btn:
    # ── Validate input — failure simulation ──────────────────────────────────────
    if not startup_idea.strip():
        st.session_state["failed_requests"] += 1
        st.session_state["total_requests"]  += 1
        log_event("VALIDATION FAILED — empty startup description", "WARNING")
        log_event(f"Failure counter incremented → {st.session_state['failed_requests']}", "ERROR")
        st.session_state["run_history"].append({
            "name": startup_name or "Empty Input",
            "decision": "ERROR", "time": 0.0, "status": "failed"
        })
        st.markdown("""
        <div class="fail-box">
          <div class="fail-box-title">✗ VALIDATION ERROR — Failure Captured</div>
          Empty startup description detected before crew was deployed.<br>
          This is an intentional failure simulation — the failure counter above has incremented.<br>
          The system caught this at validation layer, not at agent execution layer.
        </div>
        """, unsafe_allow_html=True)
        st.rerun()

    # ── Import guard ─────────────────────────────────────────────────────────────
    try:
        from crewai import Agent, Task, Crew, Process, LLM
    except ImportError as e:
        st.markdown(f'<div class="fail-box"><div class="fail-box-title">Import Error</div>{e}</div>', unsafe_allow_html=True)
        st.stop()

    api_key = os.environ.get("GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY", "")
    if not api_key:
        key_name = "GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY"
        st.markdown(f'<div class="fail-box"><div class="fail-box-title">Missing API Key</div>{key_name} not found in Streamlit Secrets.</div>', unsafe_allow_html=True)
        st.stop()

    # ── Monitoring: increment counters ────────────────────────────────────────────
    st.session_state["total_requests"] += 1
    run_number = st.session_state["total_requests"]
    sname = startup_name.strip() or "Unnamed Startup"

    # ── Logging: run start ────────────────────────────────────────────────────────
    log_event(f"=== RUN #{run_number} STARTED ===", "INFO")
    log_event(f"Startup: {sname} | Stage: {stage} | Model: {model_id.split('/')[1]}", "INFO")
    log_event(f"Investor: {investor_type} | Geography: {geography} | Depth: {depth}", "DEBUG")
    log_event(f"Input length: {len(startup_idea)} chars", "DEBUG")

    # ── Timing: start ─────────────────────────────────────────────────────────────
    t0 = time.time()

    # ── Live placeholders ─────────────────────────────────────────────────────────
    trace_ph   = st.empty()
    status_ph  = st.empty()
    timeline_ph = st.empty()

    def render_trace():
        if not show_trace:
            return
        lvl_map = {"INFO":"lvl-info","WARNING":"lvl-warn","ERROR":"lvl-error","DEBUG":"lvl-debug"}
        rows = ""
        for e in st.session_state["run_log"][-30:]:
            cls = lvl_map.get(e["level"], "lvl-debug")
            rows += (f'<div class="trace-line">'
                     f'<span class="trace-ts">{e["ts"]}</span>'
                     f'<span class="trace-lvl {cls}">{e["level"]}</span>'
                     f'<span class="trace-msg">{e["msg"]}</span></div>')
        trace_ph.markdown(f"""
        <div class="trace-shell">
          <div class="trace-titlebar">
            <span class="trace-dot td-r"></span>
            <span class="trace-dot td-y"></span>
            <span class="trace-dot td-g"></span>
            <span class="trace-title">SYSTEM TRACE LOG · REAL-TIME</span>
          </div>
          <div class="trace-body">{rows}</div>
        </div>""", unsafe_allow_html=True)

    render_trace()

    # ── Agent steps for timeline ──────────────────────────────────────────────────
    agent_steps = []

    def record_step(name, start, end, color):
        agent_steps.append({"name": name, "start": start, "end": end, "color": color})

    def render_timeline(total_elapsed=None):
        if not show_timeline or not agent_steps:
            return
        max_t = total_elapsed or max(s["end"] for s in agent_steps)
        rows = ""
        for s in agent_steps:
            dur   = round(s["end"] - s["start"], 1)
            width = int(min(((s["end"] - s["start"]) / max(max_t, 1)) * 100, 100))
            rows += f"""
            <div class="tl-row">
              <span class="tl-agent">{s['name']}</span>
              <div class="tl-bar-track">
                <div class="tl-bar-fill" style="width:{width}%;background:{s['color']}">{s['name'].split()[0]}</div>
              </div>
              <span class="tl-time">{dur}s</span>
            </div>"""
        timeline_ph.markdown(f"""
        <div class="timeline-shell">
          <div class="timeline-header">Execution Timeline — agent-level timing</div>
          <div class="timeline-body">{rows}</div>
        </div>""", unsafe_allow_html=True)

    # ── LLM ──────────────────────────────────────────────────────────────────────
    log_event("Initializing LLM...", "DEBUG")
    step_start = time.time()
    try:
        llm = LLM(model=model_id, temperature=0.3)
    except Exception as e:
        log_event(f"LLM init failed: {e}", "ERROR")
        st.markdown(f'<div class="fail-box"><div class="fail-box-title">LLM Error</div>{e}</div>', unsafe_allow_html=True)
        st.stop()
    record_step("LLM Init", step_start, time.time(), "#4ade80")
    log_event(f"LLM ready: {model_id}", "INFO")
    render_trace()

    # ── Context builders ──────────────────────────────────────────────────────────
    depth_map = {
        "Brief":    "2-3 key points per section.",
        "Standard": "Thorough analysis with supporting evidence.",
        "Detailed": "Exhaustive deep-dive. Specific estimates. Cover all sub-dimensions.",
    }
    inv_map = {
        "Venture Capital":  "Prioritize 10x return potential, TAM, and defensibility.",
        "Angel Investor":   "Prioritize team quality, traction, capital efficiency.",
        "Private Equity":   "Prioritize EBITDA path and acquisition multiples.",
        "Impact Investor":  "Balance social impact alongside financial returns.",
    }

    # ── Build agents ──────────────────────────────────────────────────────────────
    log_event("Building specialist agents...", "INFO")
    step_start = time.time()

    market_analyst = Agent(
        role="Market Analyst",
        goal="Evaluate TAM/SAM/SOM, competitive landscape, demand signals, and market timing.",
        backstory=f"Senior market analyst. {inv_map[investor_type]} Focus on {geography} markets.",
        llm=llm, verbose=True, max_iter=4,
    )
    financial_analyst = Agent(
        role="Financial Analyst",
        goal="Assess revenue model, unit economics, gross margin, capital requirements.",
        backstory="Startup CFO with 50+ financial models built. Expert in CAC, LTV, burn rate.",
        llm=llm, verbose=True, max_iter=4,
    )
    risk_analyst = Agent(
        role="Risk Analyst",
        goal="Identify and rate market, regulatory, technical, and execution risks.",
        backstory="Venture risk specialist who studied 300+ startup failures. Rates risks H/M/L.",
        llm=llm, verbose=True, max_iter=4,
    )
    investment_advisor = Agent(
        role="Investment Advisor",
        goal="Synthesize all analyses into final recommendation with JSON verdict including decision_reasoning.",
        backstory=(
            f"Senior {investor_type} partner. {inv_map[investor_type]} "
            f"Always concludes with valid JSON: market_score, financial_score, risk_score, "
            f"overall_score (0-10), confidence_level (High/Medium/Low), "
            f"final_decision (INVEST/CONDITIONAL/WATCH/PASS), "
            f"decision_reasoning (1-2 sentences explaining why)."
        ),
        llm=llm, verbose=True, max_iter=5,
    )

    record_step("Agent Setup", step_start, time.time(), "#22d3ee")
    log_event(f"4 agents ready: Market · Financial · Risk · Investment Advisor", "INFO")
    render_trace()

    # ── Build tasks ───────────────────────────────────────────────────────────────
    log_event("Defining task pipeline...", "DEBUG")
    step_start = time.time()

    market_task = Task(
        description=(
            f"MARKET ANALYSIS: {sname} ({stage})\n\n{startup_idea}\n\n"
            f"{depth_map[depth]} Geography: {geography}. "
            f"Cover: TAM/SAM/SOM, competitive landscape, demand drivers. Score /10."
        ),
        expected_output="Market analysis with TAM, competitive map, market score /10.",
        agent=market_analyst,
    )
    financial_task = Task(
        description=(
            f"FINANCIAL ANALYSIS: {sname} ({stage})\n\n{startup_idea}\n\n"
            f"{depth_map[depth]} Revenue model, CAC/LTV, gross margin, capital needs. Score /10."
        ),
        expected_output="Financial analysis with unit economics and financial score /10.",
        agent=financial_analyst,
    )
    risk_task = Task(
        description=(
            f"RISK ANALYSIS: {sname} ({stage})\n\n{startup_idea}\n\n"
            f"{depth_map[depth]} Market/regulatory/technical/execution risks. H/M/L rating. Score /10."
        ),
        expected_output="Risk matrix with severity ratings and risk score /10.",
        agent=risk_analyst,
    )
    investment_task = Task(
        description=(
            f"INVESTMENT RECOMMENDATION: {sname} ({stage})\n\n"
            f"{depth_map[depth]} Synthesize all three analyses. Include decision reasoning.\n\n"
            f"END with EXACTLY this JSON:\n```json\n"
            f'{{\n'
            f'  "startup_name": "{sname}",\n'
            f'  "market_score": <0-10>,\n'
            f'  "financial_score": <0-10>,\n'
            f'  "risk_score": <0-10>,\n'
            f'  "overall_score": <0-10>,\n'
            f'  "confidence_level": "<High|Medium|Low>",\n'
            f'  "final_decision": "<INVEST|CONDITIONAL|WATCH|PASS>",\n'
            f'  "decision_reasoning": "<1-2 sentences explaining the decision>"\n'
            f'}}\n```'
        ),
        expected_output="Investment memo with JSON verdict including decision_reasoning.",
        agent=investment_advisor,
        context=[market_task, financial_task, risk_task],
    )

    crew = Crew(
        agents=[market_analyst, financial_analyst, risk_analyst, investment_advisor],
        tasks=[market_task, financial_task, risk_task, investment_task],
        process=Process.sequential,
        verbose=False,
    )

    record_step("Task Pipeline", step_start, time.time(), "#a78bfa")
    log_event("4 tasks configured: Market → Financial → Risk → Investment", "INFO")
    render_trace()

    status_ph.markdown(
        '<div style="font-family:var(--mono);font-size:0.75rem;color:var(--text3);'
        'margin-bottom:1rem;letter-spacing:0.06em">'
        '⟳ AGENTS RUNNING — trace updating in real time...</div>',
        unsafe_allow_html=True
    )

    # ── Execute ───────────────────────────────────────────────────────────────────
    log_event("Crew execution started...", "INFO")
    exec_start = time.time()
    render_trace()

    try:
        result = crew.kickoff()
        exec_end = time.time()
        exec_time = round(exec_end - exec_start, 2)
        total_time = round(time.time() - t0, 2)

        record_step("Market Analysis",     exec_start,                exec_start + exec_time*0.25, "#fbbf24")
        record_step("Financial Analysis",  exec_start + exec_time*0.25, exec_start + exec_time*0.50, "#60a5fa")
        record_step("Risk Assessment",     exec_start + exec_time*0.50, exec_start + exec_time*0.75, "#f87171")
        record_step("Investment Verdict",  exec_start + exec_time*0.75, exec_end,                    "#4ade80")

        # ── Monitoring: update counters ───────────────────────────────────────────
        st.session_state["total_time"] += total_time
        log_event(f"Crew complete · exec_time={exec_time}s · total_time={total_time}s", "INFO")

        # ── Parse outputs ─────────────────────────────────────────────────────────
        def safe_out(task):
            try:   return str(task.output).strip() if task.output else ""
            except: return ""

        market_out     = safe_out(market_task)
        financial_out  = safe_out(financial_task)
        risk_out       = safe_out(risk_task)
        investment_out = safe_out(investment_task)
        full_result    = str(result).strip()

        log_event(f"Market output: {len(market_out)} chars", "DEBUG")
        log_event(f"Financial output: {len(financial_out)} chars", "DEBUG")
        log_event(f"Risk output: {len(risk_out)} chars", "DEBUG")
        log_event(f"Investment output: {len(investment_out)} chars", "DEBUG")

        # ── Parse JSON ────────────────────────────────────────────────────────────
        log_event("Extracting JSON verdict...", "INFO")
        verdict = {}
        search_text = investment_out + "\n" + full_result
        m = re.search(r'```json\s*(\{.*?\})\s*```', search_text, re.DOTALL)
        if not m:
            m = re.search(r'(\{[^{}]*"final_decision"[^{}]*\})', search_text, re.DOTALL)
        if m:
            try:
                verdict = json.loads(m.group(1))
                log_event(f"JSON parsed OK · decision={verdict.get('final_decision','?')} · confidence={verdict.get('confidence_level','?')}", "INFO")
            except Exception as je:
                log_event(f"JSON parse error: {je}", "WARNING")
        else:
            log_event("JSON block not found in output — regex fallback failed", "WARNING")

        # ── Validate output ───────────────────────────────────────────────────────
        required_keys = ["final_decision","overall_score","decision_reasoning"]
        missing = [k for k in required_keys if k not in verdict]
        if missing:
            log_event(f"Validation WARNING — missing fields: {missing}", "WARNING")
        else:
            log_event("Output validation passed — all required fields present", "INFO")

        decision   = verdict.get("final_decision", "—")
        ms         = verdict.get("market_score",    "—")
        fs         = verdict.get("financial_score", "—")
        rs         = verdict.get("risk_score",      "—")
        os_        = verdict.get("overall_score",   "—")
        conf       = verdict.get("confidence_level","—")
        reasoning  = verdict.get("decision_reasoning", "")

        # ── Run history ───────────────────────────────────────────────────────────
        st.session_state["run_history"].append({
            "name": sname, "decision": decision,
            "time": total_time, "status": "ok"
        })
        log_event(f"=== RUN #{run_number} COMPLETE · decision={decision} · time={total_time}s ===", "INFO")

        render_trace()
        render_timeline(total_time)
        status_ph.empty()

        # ── VERDICT UI ────────────────────────────────────────────────────────────
        st.markdown('<div class="div-green"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-label">Investment Verdict</div>', unsafe_allow_html=True)

        chip_map = {
            "INVEST":"chip-invest", "CONDITIONAL":"chip-cond",
            "WATCH":"chip-watch",   "PASS":"chip-pass",
        }
        chip_cls = chip_map.get(decision, "chip-watch")
        chip_lbl = {"INVEST":"↑ INVEST","CONDITIONAL":"◎ CONDITIONAL","WATCH":"◉ WATCH","PASS":"↓ PASS"}.get(decision, decision)

        st.markdown(f"""
        <div class="score-grid">
          <div class="score-cell sc-a"><div class="score-num">{ms}<span style="font-size:0.9rem">/10</span></div><div class="score-lbl">Market</div></div>
          <div class="score-cell sc-b"><div class="score-num">{fs}<span style="font-size:0.9rem">/10</span></div><div class="score-lbl">Financial</div></div>
          <div class="score-cell sc-r"><div class="score-num">{rs}<span style="font-size:0.9rem">/10</span></div><div class="score-lbl">Risk</div></div>
          <div class="score-cell sc-g"><div class="score-num">{os_}<span style="font-size:0.9rem">/10</span></div><div class="score-lbl">Overall</div></div>
        </div>
        <div class="decision-row">
          <span class="decision-chip {chip_cls}">{chip_lbl}</span>
          <span class="confidence-tag">CONFIDENCE: {conf}</span>
          <span class="confidence-tag">RUN #{run_number}</span>
          <span class="confidence-tag">{total_time}s</span>
        </div>
        """, unsafe_allow_html=True)

        # Decision reasoning — the Day 11 explainability feature
        if reasoning:
            st.markdown(f"""
            <div class="reasoning-box">
              <span class="reasoning-label">◈ Decision Reasoning — Explainability Layer</span>
              {reasoning}
            </div>
            """, unsafe_allow_html=True)

        # ── Report sections ────────────────────────────────────────────────────────
        sections = [
            ("📊","vi-amber","Market Analysis",           "Market Analyst",     market_out     or full_result),
            ("💰","vi-green","Financial Analysis",         "Financial Analyst",  financial_out  or full_result),
            ("⚠️","vi-red",  "Risk Assessment",            "Risk Analyst",       risk_out       or full_result),
            ("🎯","vi-green","Investment Recommendation",  "Investment Advisor", investment_out or full_result),
        ]
        for icon, vi_cls, title, agent_lbl, content in sections:
            if not content: continue
            st.markdown(f"""
            <div class="verdict-card">
              <div class="verdict-header">
                <div class="verdict-icon {vi_cls}">{icon}</div>
                <span class="verdict-title">{title}</span>
                <span class="verdict-agent">{agent_lbl}</span>
              </div>
              <div class="verdict-body">{content.replace(chr(10),'<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── JSON verdict ──────────────────────────────────────────────────────────
        if show_json and verdict:
            st.markdown('<div class="sec-label" style="margin-top:1.25rem">Structured JSON Output</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="json-shell">
              <div class="json-bar">
                <span class="json-bar-title">DECISION PAYLOAD · MACHINE-READABLE</span>
                <span class="json-valid">✓ VALID JSON</span>
              </div>
              <div class="json-body"><pre>{json.dumps(verdict, indent=2)}</pre></div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        exec_time = round(time.time() - exec_start, 2)
        st.session_state["failed_requests"] += 1
        log_event(f"EXECUTION ERROR after {exec_time}s: {str(e)[:120]}", "ERROR")
        log_event(f"Failure counter → {st.session_state['failed_requests']}", "ERROR")
        st.session_state["run_history"].append({
            "name": sname, "decision": "ERROR", "time": exec_time, "status": "failed"
        })
        render_trace()
        status_ph.empty()
        st.markdown(f"""
        <div class="fail-box">
          <div class="fail-box-title">✗ AGENT EXECUTION ERROR — Failure Logged</div>
          {str(e)}<br><br>
          <span style="color:var(--text3)">Failure #{st.session_state['failed_requests']} recorded · Run time: {exec_time}s</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════════
# FULL TRACE LOG (persistent across runs)
# ══════════════════════════════════════════════════════════════════════════════════
if st.session_state["run_log"] and not run_btn:
    st.markdown('<div class="sec-label">Full Session Trace Log</div>', unsafe_allow_html=True)
    lvl_map = {"INFO":"lvl-info","WARNING":"lvl-warn","ERROR":"lvl-error","DEBUG":"lvl-debug"}
    rows = ""
    for e in st.session_state["run_log"]:
        cls = lvl_map.get(e["level"], "lvl-debug")
        rows += (f'<div class="trace-line">'
                 f'<span class="trace-ts">{e["ts"]}</span>'
                 f'<span class="trace-lvl {cls}">{e["level"]}</span>'
                 f'<span class="trace-msg">{e["msg"]}</span></div>')
    st.markdown(f"""
    <div class="trace-shell">
      <div class="trace-titlebar">
        <span class="trace-dot td-r"></span>
        <span class="trace-dot td-y"></span>
        <span class="trace-dot td-g"></span>
        <span class="trace-title">FULL SESSION LOG · {len(st.session_state['run_log'])} EVENTS</span>
      </div>
      <div class="trace-body" style="max-height:380px">{rows}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="div" style="margin-top:2rem"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="obs-footer">
  <span>agent-forge · day 11 of 15</span>
  <span>logging · monitoring · tracing · explainability</span>
  <span>crewai · gemini 2.5 flash</span>
</div>
""", unsafe_allow_html=True)
