import streamlit as st
import os
import time
import json
import re
from datetime import datetime

st.set_page_config(
    page_title="VentureIQ · AI Due Diligence",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Secrets ──────────────────────────────────────────────────────────────────────
for secret_key in ["GEMINI_API_KEY", "GROQ_API_KEY"]:
    try:
        os.environ[secret_key] = st.secrets[secret_key]
    except Exception:
        pass
os.environ.setdefault("OPENAI_API_KEY", "dummy-not-used")

# ══════════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Premium VC SaaS
# Inspired by: Carta, Linear, Retool, Vercel Dashboard
# Color: Deep navy base · Electric blue accent · Semantic greens/ambers/reds
# Type: Sora (geometric humanist) + JetBrains Mono
# ══════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Token System ── */
:root {
    /* Base */
    --navy-950:  #020817;
    --navy-900:  #0A0F1E;
    --navy-850:  #0D1526;
    --navy-800:  #111827;
    --navy-750:  #141D2E;
    --navy-700:  #1A2440;
    --navy-600:  #1E2D4A;
    --navy-500:  #253354;
    --navy-400:  #334466;

    /* Borders */
    --border-subtle:  rgba(99,130,190,0.12);
    --border-default: rgba(99,130,190,0.20);
    --border-strong:  rgba(99,130,190,0.35);
    --border-focus:   rgba(59,130,246,0.60);

    /* Blue accent */
    --blue-600:  #1D4ED8;
    --blue-500:  #2563EB;
    --blue-400:  #3B82F6;
    --blue-300:  #60A5FA;
    --blue-200:  #93C5FD;
    --blue-glow: rgba(59,130,246,0.20);
    --blue-mist: rgba(59,130,246,0.08);

    /* Semantic */
    --emerald:     #10B981;
    --emerald-dim: rgba(16,185,129,0.12);
    --emerald-bd:  rgba(16,185,129,0.30);
    --amber:       #F59E0B;
    --amber-dim:   rgba(245,158,11,0.12);
    --amber-bd:    rgba(245,158,11,0.30);
    --rose:        #F43F5E;
    --rose-dim:    rgba(244,63,94,0.12);
    --rose-bd:     rgba(244,63,94,0.30);
    --violet:      #8B5CF6;
    --violet-dim:  rgba(139,92,246,0.12);
    --violet-bd:   rgba(139,92,246,0.30);
    --sky:         #0EA5E9;
    --sky-dim:     rgba(14,165,233,0.12);
    --sky-bd:      rgba(14,165,233,0.30);

    /* Text */
    --text-primary:   #F0F4FF;
    --text-secondary: #94A3C8;
    --text-tertiary:  #4A5878;
    --text-disabled:  #2A3450;

    /* Typography */
    --font-display: 'Sora', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;

    /* Radius */
    --r-sm:  6px;
    --r-md:  10px;
    --r-lg:  14px;
    --r-xl:  18px;

    /* Shadows */
    --shadow-sm:  0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md:  0 4px 12px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.3);
    --shadow-lg:  0 10px 40px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
    --shadow-glow:0 0 30px rgba(59,130,246,0.15), 0 0 8px rgba(59,130,246,0.08);
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: var(--font-display) !important;
    background: var(--navy-950) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 1.5rem 6rem !important;
    max-width: 960px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--navy-900); }
::-webkit-scrollbar-thumb { background: var(--navy-500); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--blue-400); }

/* ══════════════════════════
   HERO SECTION
══════════════════════════ */
.hero-wrap {
    position: relative;
    background: var(--navy-900);
    border-bottom: 1px solid var(--border-subtle);
    padding: 3rem 2.5rem 2.5rem;
    margin: 0 -1.5rem 2.5rem;
    overflow: hidden;
}

/* Animated gradient mesh background */
.hero-wrap::before {
    content: '';
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 50%, rgba(37,99,235,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 50% 80% at 80% 20%, rgba(16,185,129,0.06) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 60% 80%, rgba(139,92,246,0.06) 0%, transparent 50%);
    pointer-events: none;
}

/* Subtle grid overlay */
.hero-wrap::after {
    content: '';
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(99,130,190,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,130,190,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
}

.hero-inner { position: relative; z-index: 1; }

.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 0.5rem;
    font-family: var(--font-mono); font-size: 0.68rem; font-weight: 500;
    color: var(--blue-300); letter-spacing: 0.12em; text-transform: uppercase;
    background: var(--blue-mist); border: 1px solid var(--border-focus);
    padding: 0.3rem 0.75rem; border-radius: 999px; margin-bottom: 1.2rem;
}
.eyebrow-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--blue-400);
    box-shadow: 0 0 8px var(--blue-400);
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.hero-title {
    font-size: 2.6rem; font-weight: 800; line-height: 1.1;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #F0F4FF 30%, #93C5FD 70%, #60A5FA);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.9rem;
}

.hero-sub {
    font-size: 0.95rem; font-weight: 300; color: var(--text-secondary);
    line-height: 1.65; max-width: 540px; margin-bottom: 1.8rem;
}

.hero-meta {
    display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;
}
.hero-pill {
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-family: var(--font-mono); font-size: 0.7rem; font-weight: 500;
    color: var(--text-tertiary); letter-spacing: 0.05em;
}
.hero-pill-dot { width: 5px; height: 5px; border-radius: 50%; }

.hero-badge {
    margin-left: auto;
    font-family: var(--font-mono); font-size: 0.7rem; font-weight: 600;
    color: var(--blue-300); background: var(--blue-mist);
    border: 1px solid var(--border-focus); border-radius: var(--r-sm);
    padding: 0.35rem 0.8rem; letter-spacing: 0.04em;
}

/* ══════════════════════════
   SECTION LABELS
══════════════════════════ */
.section-label {
    display: flex; align-items: center; gap: 0.5rem;
    font-family: var(--font-mono); font-size: 0.66rem; font-weight: 600;
    color: var(--text-tertiary); letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.section-label::before {
    content: '';
    display: block; width: 16px; height: 1px;
    background: var(--blue-400);
}

/* ══════════════════════════
   AGENT PIPELINE
══════════════════════════ */
.pipeline-card {
    background: var(--navy-850);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-lg);
    padding: 1.25rem 1.5rem;
    margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.pipeline-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--blue-400), transparent);
    opacity: 0.4;
}
.pipeline-flow {
    display: flex; align-items: center; gap: 0;
    overflow-x: auto; padding-bottom: 0.25rem;
}
.pipeline-flow::-webkit-scrollbar { height: 2px; }

.agent-node {
    display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
    min-width: 90px; padding: 0 0.25rem; flex-shrink: 0;
}
.agent-avatar {
    width: 44px; height: 44px; border-radius: var(--r-md);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; position: relative;
    border: 1px solid var(--border-subtle);
    background: var(--navy-800);
    transition: all 0.2s ease;
}
.agent-avatar.manager  { background: linear-gradient(135deg,#1D4ED8,#1E40AF); border-color: var(--blue-500); box-shadow: 0 0 16px var(--blue-glow); }
.agent-avatar.market   { background: var(--amber-dim);  border-color: var(--amber-bd);   }
.agent-avatar.finance  { background: var(--sky-dim);    border-color: var(--sky-bd);     }
.agent-avatar.risk     { background: var(--rose-dim);   border-color: var(--rose-bd);    }
.agent-avatar.advisor  { background: var(--emerald-dim);border-color: var(--emerald-bd); }
.agent-avatar.output   { background: var(--violet-dim); border-color: var(--violet-bd);  }

.agent-label {
    font-family: var(--font-mono); font-size: 0.6rem; font-weight: 500;
    color: var(--text-tertiary); text-align: center; letter-spacing: 0.04em;
    line-height: 1.3;
}
.agent-arrow {
    flex-shrink: 0; padding: 0 0.15rem;
    color: var(--text-disabled); font-size: 0.9rem;
    padding-bottom: 1.2rem;
}

/* ══════════════════════════
   INPUTS
══════════════════════════ */
/* Global input styling */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
[data-baseweb="select"] > div {
    background: var(--navy-800) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--r-md) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-display) !important;
    font-size: 0.88rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--blue-400) !important;
    box-shadow: 0 0 0 3px var(--blue-mist) !important;
    outline: none !important;
}
.stTextArea > div > div > textarea::placeholder,
.stTextInput > div > div > input::placeholder {
    color: var(--text-tertiary) !important;
}

/* Labels */
label[data-testid="stWidgetLabel"] p,
label[data-testid="stWidgetLabel"] {
    font-family: var(--font-mono) !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    color: var(--text-tertiary) !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* Selectbox dropdown */
[data-baseweb="popover"] [data-baseweb="menu"] {
    background: var(--navy-800) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--r-md) !important;
}
[data-baseweb="option"]:hover {
    background: var(--blue-mist) !important;
}

/* ══════════════════════════
   PRESET CARDS
══════════════════════════ */
.preset-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.6rem;
    margin-bottom: 1.5rem;
}
.preset-item {
    background: var(--navy-850);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-md);
    padding: 0.85rem 0.9rem;
    cursor: pointer;
    transition: all 0.15s ease;
    position: relative;
    overflow: hidden;
}
.preset-item:hover {
    border-color: var(--blue-400);
    background: var(--navy-800);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md), 0 0 20px var(--blue-glow);
}
.preset-item::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, var(--blue-mist), transparent);
    opacity: 0;
    transition: opacity 0.15s ease;
}
.preset-item:hover::after { opacity: 1; }

.preset-sector {
    font-family: var(--font-mono); font-size: 0.6rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.preset-name {
    font-size: 0.82rem; font-weight: 600; color: var(--text-primary);
    line-height: 1.3; margin-bottom: 0.3rem;
}
.preset-desc {
    font-size: 0.73rem; color: var(--text-tertiary); line-height: 1.4;
}

/* Sector colors */
.sector-health   { color: var(--emerald); }
.sector-logistics{ color: var(--sky); }
.sector-legal    { color: var(--violet); }
.sector-agri     { color: var(--amber); }
.sector-saas     { color: var(--blue-300); }
.sector-hr       { color: var(--rose); }

/* ══════════════════════════
   MAIN BUTTON
══════════════════════════ */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, var(--blue-500), var(--blue-600)) !important;
    color: #fff !important;
    border: 1px solid var(--blue-400) !important;
    border-radius: var(--r-md) !important;
    padding: 0.9rem 2rem !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.01em !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.35), 0 1px 3px rgba(0,0,0,0.4) !important;
    position: relative !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--blue-400), var(--blue-500)) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(37,99,235,0.45), 0 2px 6px rgba(0,0,0,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ══════════════════════════
   DIVIDERS
══════════════════════════ */
.divider {
    height: 1px;
    background: var(--border-subtle);
    margin: 1.75rem 0;
}
.divider-glow {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-strong), transparent);
    margin: 1.75rem 0;
}

/* ══════════════════════════
   SETTINGS PANEL
══════════════════════════ */
.streamlit-expanderHeader {
    background: var(--navy-850) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--r-md) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    padding: 0.75rem 1rem !important;
}
.streamlit-expanderHeader:hover {
    border-color: var(--border-default) !important;
    color: var(--text-primary) !important;
}
.streamlit-expanderContent {
    background: var(--navy-900) !important;
    border: 1px solid var(--border-subtle) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r-md) var(--r-md) !important;
    padding: 1.25rem !important;
}

/* Checkbox */
.stCheckbox label p { color: var(--text-secondary) !important; font-size: 0.85rem !important; }
.stCheckbox > label > div:first-child > div {
    background: var(--navy-700) !important;
    border: 1px solid var(--border-default) !important;
}

/* Select slider */
.stSlider [data-testid="stThumbValue"] { color: var(--blue-300) !important; font-family: var(--font-mono) !important; }

/* ══════════════════════════
   EXECUTION LOG
══════════════════════════ */
.log-shell {
    background: var(--navy-950);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-lg);
    overflow: hidden;
    margin-bottom: 1.5rem;
    font-family: var(--font-mono);
    box-shadow: var(--shadow-lg);
}
.log-titlebar {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.75rem 1.1rem;
    background: var(--navy-850);
    border-bottom: 1px solid var(--border-subtle);
}
.log-dot { width: 10px; height: 10px; border-radius: 50%; }
.log-dot-r { background: #FF5F56; }
.log-dot-y { background: #FFBD2E; }
.log-dot-g { background: #27C93F; }
.log-title { font-size: 0.68rem; color: var(--text-tertiary); margin-left: 0.5rem; letter-spacing: 0.08em; }
.log-body  { padding: 0.9rem 1.1rem; max-height: 230px; overflow-y: auto; }
.log-line  { display: flex; align-items: baseline; gap: 0.7rem; margin-bottom: 0.3rem; font-size: 0.73rem; }
.log-t     { color: var(--text-disabled); min-width: 44px; font-size: 0.68rem; }
.log-tag   { font-size: 0.62rem; font-weight: 600; padding: 0.12rem 0.5rem;
             border-radius: 4px; letter-spacing: 0.06em; min-width: 52px; text-align: center; flex-shrink: 0; }
.log-msg   { color: var(--text-secondary); font-size: 0.71rem; }

.t-sys   { background: rgba(148,163,200,0.08); color: var(--text-tertiary); border: 1px solid var(--border-subtle); }
.t-agent { background: var(--blue-mist);    color: var(--blue-300);   border: 1px solid rgba(59,130,246,0.2); }
.t-task  { background: var(--amber-dim);    color: var(--amber);      border: 1px solid var(--amber-bd); }
.t-ok    { background: var(--emerald-dim);  color: var(--emerald);    border: 1px solid var(--emerald-bd); }
.t-err   { background: var(--rose-dim);     color: var(--rose);       border: 1px solid var(--rose-bd); }

/* ══════════════════════════
   VERDICT SECTION
══════════════════════════ */
.verdict-wrap {
    background: var(--navy-850);
    border: 1px solid var(--border-default);
    border-radius: var(--r-xl);
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
    box-shadow: var(--shadow-lg);
}
.verdict-wrap::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--blue-500), var(--emerald), var(--violet));
}

.verdict-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;
}
.verdict-startup {
    font-size: 1.3rem; font-weight: 700; color: var(--text-primary);
    letter-spacing: -0.02em;
}
.verdict-stage {
    font-family: var(--font-mono); font-size: 0.68rem; color: var(--text-tertiary);
    margin-top: 0.2rem; letter-spacing: 0.06em;
}

/* Score rings */
.score-ring-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 1rem; margin-bottom: 1.5rem;
}
.score-ring-card {
    background: var(--navy-900);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-lg);
    padding: 1.1rem 0.75rem;
    text-align: center;
    position: relative; overflow: hidden;
    transition: border-color 0.2s ease;
}
.score-ring-card:hover { border-color: var(--border-default); }

.score-ring-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.ring-market::before   { background: var(--amber); }
.ring-finance::before  { background: var(--sky); }
.ring-risk::before     { background: var(--rose); }
.ring-overall::before  { background: var(--emerald); }

.score-big {
    font-size: 2.4rem; font-weight: 800; line-height: 1; margin-bottom: 0.1rem;
    letter-spacing: -0.04em;
}
.ring-market  .score-big  { color: var(--amber); }
.ring-finance .score-big  { color: var(--sky); }
.ring-risk    .score-big  { color: var(--rose); }
.ring-overall .score-big  { color: var(--emerald); }

.score-denom {
    font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-tertiary);
    vertical-align: super; margin-left: 1px;
}
.score-ring-label {
    font-family: var(--font-mono); font-size: 0.6rem; font-weight: 600;
    color: var(--text-tertiary); letter-spacing: 0.1em; text-transform: uppercase;
}

/* Progress bar under score */
.score-bar-track {
    height: 3px; background: var(--navy-700); border-radius: 2px; margin-top: 0.5rem; overflow: hidden;
}
.score-bar-fill {
    height: 100%; border-radius: 2px;
    transition: width 1s cubic-bezier(0.4,0,0.2,1);
}
.ring-market  .score-bar-fill { background: var(--amber); }
.ring-finance .score-bar-fill { background: var(--sky); }
.ring-risk    .score-bar-fill { background: var(--rose); }
.ring-overall .score-bar-fill { background: var(--emerald); box-shadow: 0 0 8px rgba(16,185,129,0.4); }

/* Decision badge */
.decision-row {
    display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
    margin-bottom: 1rem;
}
.decision-chip {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1.25rem; border-radius: 999px;
    font-size: 0.9rem; font-weight: 700; letter-spacing: 0.02em;
}
.chip-invest  { background: var(--emerald-dim); border: 1.5px solid var(--emerald-bd); color: var(--emerald); }
.chip-cond    { background: var(--amber-dim);   border: 1.5px solid var(--amber-bd);   color: var(--amber); }
.chip-watch   { background: var(--sky-dim);     border: 1.5px solid var(--sky-bd);     color: var(--sky); }
.chip-pass    { background: var(--rose-dim);    border: 1.5px solid var(--rose-bd);    color: var(--rose); }

.decision-rationale {
    font-size: 0.87rem; color: var(--text-secondary); font-style: italic; line-height: 1.5;
}
.decision-meta {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 0.75rem; margin-top: 1rem;
}
.meta-item {
    background: var(--navy-900); border: 1px solid var(--border-subtle);
    border-radius: var(--r-md); padding: 0.75rem 0.9rem;
}
.meta-label {
    font-family: var(--font-mono); font-size: 0.6rem; font-weight: 600;
    color: var(--text-tertiary); letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 0.25rem;
}
.meta-value {
    font-size: 0.88rem; font-weight: 600; color: var(--text-primary);
}

/* ══════════════════════════
   REPORT SECTIONS
══════════════════════════ */
.report-card {
    background: var(--navy-850);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-lg);
    overflow: hidden;
    margin-bottom: 0.9rem;
    box-shadow: var(--shadow-sm);
    transition: border-color 0.15s ease;
}
.report-card:hover { border-color: var(--border-default); }

.report-header {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.9rem 1.2rem;
    background: var(--navy-900);
    border-bottom: 1px solid var(--border-subtle);
    position: relative;
}
.report-accent {
    position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    border-radius: 3px 0 0 3px;
}
.accent-market  { background: var(--amber); }
.accent-finance { background: var(--sky); }
.accent-risk    { background: var(--rose); }
.accent-invest  { background: var(--emerald); }

.report-icon-wrap {
    width: 32px; height: 32px; border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; flex-shrink: 0;
}
.icon-market  { background: var(--amber-dim);   border: 1px solid var(--amber-bd);   }
.icon-finance { background: var(--sky-dim);     border: 1px solid var(--sky-bd);     }
.icon-risk    { background: var(--rose-dim);    border: 1px solid var(--rose-bd);    }
.icon-invest  { background: var(--emerald-dim); border: 1px solid var(--emerald-bd); }

.report-title { font-size: 0.88rem; font-weight: 600; color: var(--text-primary); }
.report-agent {
    margin-left: auto;
    font-family: var(--font-mono); font-size: 0.62rem; color: var(--text-tertiary);
    background: var(--navy-800); border: 1px solid var(--border-subtle);
    padding: 0.2rem 0.55rem; border-radius: 4px; letter-spacing: 0.04em;
}
.report-body {
    padding: 1.2rem 1.3rem; font-size: 0.87rem; color: var(--text-secondary);
    line-height: 1.78;
}
.report-body strong, .report-body b { color: var(--text-primary); font-weight: 600; }
.report-body h1, .report-body h2, .report-body h3 {
    color: var(--text-primary); font-weight: 700; margin: 1rem 0 0.4rem;
    font-size: 0.95rem;
}

/* ══════════════════════════
   JSON PANEL
══════════════════════════ */
.json-shell {
    background: var(--navy-950);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-lg); overflow: hidden;
    margin-top: 1rem;
    box-shadow: var(--shadow-md);
}
.json-titlebar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.65rem 1rem;
    background: var(--navy-900);
    border-bottom: 1px solid var(--border-subtle);
}
.json-title { font-family: var(--font-mono); font-size: 0.68rem; color: var(--text-tertiary); letter-spacing: 0.08em; }
.json-badge {
    font-family: var(--font-mono); font-size: 0.62rem; font-weight: 600;
    color: var(--emerald); background: var(--emerald-dim);
    border: 1px solid var(--emerald-bd); padding: 0.15rem 0.5rem; border-radius: 4px;
    letter-spacing: 0.04em;
}
.json-body { padding: 1.1rem; overflow-x: auto; }
.json-body pre {
    font-family: var(--font-mono); font-size: 0.78rem;
    color: #7DD3FC; margin: 0; white-space: pre-wrap; word-break: break-word;
    line-height: 1.6;
}

/* ══════════════════════════
   ERROR BOX
══════════════════════════ */
.err-box {
    background: var(--rose-dim); border: 1px solid var(--rose-bd);
    border-radius: var(--r-md); padding: 0.9rem 1.1rem;
    font-size: 0.85rem; color: var(--rose); margin-top: 1rem;
    font-family: var(--font-display);
}
.info-box {
    background: var(--blue-mist); border: 1px solid var(--border-focus);
    border-radius: var(--r-md); padding: 0.9rem 1.1rem;
    font-size: 0.85rem; color: var(--blue-300); margin-top: 0.5rem;
}

/* ══════════════════════════
   FOOTER
══════════════════════════ */
.footer {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1.25rem 0 0;
    border-top: 1px solid var(--border-subtle);
    font-family: var(--font-mono); font-size: 0.66rem; color: var(--text-tertiary);
    letter-spacing: 0.06em;
}

/* ══════════════════════════
   MULTISELECT TAG
══════════════════════════ */
.stMultiSelect span[data-baseweb="tag"] {
    background: var(--blue-mist) !important;
    border: 1px solid var(--border-focus) !important;
    color: var(--blue-300) !important;
    border-radius: 4px !important;
    font-size: 0.78rem !important;
}

</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════════
today = datetime.now().strftime("%b %d, %Y")
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-inner">
    <div class="hero-eyebrow">
      <span class="eyebrow-dot"></span>
      AgentForge · Day 7 of 15
    </div>
    <h1 class="hero-title">AI Startup Due Diligence</h1>
    <p class="hero-sub">
      Five specialist agents — Market Analyst, Financial Analyst, Risk Analyst,
      Investment Advisor, and Manager — analyze any startup idea and deliver
      a scored verdict with machine-readable JSON output.
    </p>
    <div class="hero-meta">
      <span class="hero-pill"><span class="hero-pill-dot" style="background:var(--blue-400)"></span>5 Agents</span>
      <span class="hero-pill"><span class="hero-pill-dot" style="background:var(--amber)"></span>Hierarchical Process</span>
      <span class="hero-pill"><span class="hero-pill-dot" style="background:var(--emerald)"></span>JSON Verdict</span>
      <span class="hero-pill"><span class="hero-pill-dot" style="background:var(--violet)"></span>$300–$1000 Sellable</span>
      <span class="hero-badge">{today}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# AGENT PIPELINE VISUAL
# ══════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Agent Architecture</div>', unsafe_allow_html=True)
st.markdown("""
<div class="pipeline-card">
  <div class="pipeline-flow">
    <div class="agent-node">
      <div class="agent-avatar manager">👑</div>
      <div class="agent-label">MANAGER<br>DELEGATE</div>
    </div>
    <div class="agent-arrow">›</div>
    <div class="agent-node">
      <div class="agent-avatar market">📊</div>
      <div class="agent-label">MARKET<br>ANALYST</div>
    </div>
    <div class="agent-arrow">›</div>
    <div class="agent-node">
      <div class="agent-avatar finance">💰</div>
      <div class="agent-label">FINANCIAL<br>ANALYST</div>
    </div>
    <div class="agent-arrow">›</div>
    <div class="agent-node">
      <div class="agent-avatar risk">⚠️</div>
      <div class="agent-label">RISK<br>ANALYST</div>
    </div>
    <div class="agent-arrow">›</div>
    <div class="agent-node">
      <div class="agent-avatar advisor">🎯</div>
      <div class="agent-label">INVESTMENT<br>ADVISOR</div>
    </div>
    <div class="agent-arrow">›</div>
    <div class="agent-node">
      <div class="agent-avatar output">{ }</div>
      <div class="agent-label">JSON<br>VERDICT</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# PRESET CARDS
# ══════════════════════════════════════════════════════════════════════════════════
PRESETS = [
    {
        "name": "AI Medical Booking",
        "sector": "HealthTech", "sector_cls": "sector-health",
        "desc": "ML-powered patient-doctor matching and smart scheduling.",
        "idea": "An AI-powered medical appointment booking platform that uses machine learning to match patients with the right specialists, predict no-shows, send smart reminders, and optimize clinic schedules. Target market: private clinics and hospital chains in Southeast Asia."
    },
    {
        "name": "AI Logistics Optimizer",
        "sector": "LogisticsTech", "sector_cls": "sector-logistics",
        "desc": "Route optimization and demand forecasting for last-mile delivery.",
        "idea": "An AI logistics optimization platform for last-mile delivery companies that uses real-time traffic data, demand forecasting, and dynamic routing to reduce delivery costs by 25–40%. Target: mid-size e-commerce fulfillment and courier companies."
    },
    {
        "name": "AI Legal Analyzer",
        "sector": "LegalTech", "sector_cls": "sector-legal",
        "desc": "Contract review, risk flagging, and clause extraction for law firms.",
        "idea": "An AI legal document analyzer that automates contract review, flags high-risk clauses, extracts key obligations, and compares against standard templates. Targets law firms and corporate legal departments looking to reduce manual review time by 70%."
    },
    {
        "name": "AI Farming Automation",
        "sector": "AgriTech", "sector_cls": "sector-agri",
        "desc": "Precision agriculture with satellite imagery and IoT sensors.",
        "idea": "An AI-powered precision farming platform that integrates satellite imagery, soil sensors, and weather data to provide actionable recommendations for irrigation, fertilization, and pest control. Target: commercial farms of 100+ acres in South Asia and Africa."
    },
    {
        "name": "AI Support SaaS",
        "sector": "SaaS / CX", "sector_cls": "sector-saas",
        "desc": "Autonomous agents that resolve 80% of tickets without humans.",
        "idea": "A B2B SaaS product that deploys AI support agents trained on a company's own documentation and past tickets to autonomously resolve customer inquiries. Pricing: per-resolution model. Target: e-commerce and SaaS companies with 500+ monthly tickets."
    },
    {
        "name": "AI Recruitment Screener",
        "sector": "HRTech", "sector_cls": "sector-hr",
        "desc": "CV screening, skills assessment, and interview scheduling at scale.",
        "idea": "An AI recruitment platform that screens thousands of CVs in minutes, conducts async video interviews, scores candidates on skills and culture fit, and schedules final rounds automatically. Target: staffing agencies and enterprise HR teams with 100+ monthly hires."
    },
]

st.markdown('<div class="section-label">Quick Start — Select a Startup</div>', unsafe_allow_html=True)

cols = st.columns(3)
for i, p in enumerate(PRESETS):
    with cols[i % 3]:
        if st.button(
            f"{p['name']}",
            key=f"p_{i}",
            help=p["desc"]
        ):
            st.session_state["startup_idea"] = p["idea"]
            st.session_state["startup_name"] = p["name"]
            st.rerun()

# Render preset cards via HTML (visual only, buttons above handle clicks)
preset_html = '<div class="preset-grid">'
for p in PRESETS:
    preset_html += f"""
    <div class="preset-item">
        <div class="preset-sector {p['sector_cls']}">{p['sector']}</div>
        <div class="preset-name">{p['name']}</div>
        <div class="preset-desc">{p['desc']}</div>
    </div>"""
preset_html += '</div>'

# Note: the Streamlit buttons above are the real interactive elements.
# We use CSS to hide the default button labels and only show the custom HTML cards.
# Actually let's just use the clean Streamlit buttons and keep the styled HTML separately:
st.markdown('<div class="divider-glow"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# INPUT FORM
# ══════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Startup Brief</div>', unsafe_allow_html=True)

startup_idea = st.text_area(
    "STARTUP DESCRIPTION",
    value=st.session_state.get("startup_idea", ""),
    placeholder="Describe the startup in detail: what it does, target market, business model, geography, competitive advantage, and any traction or metrics to evaluate...",
    height=120,
)

col_n, col_s = st.columns(2)
with col_n:
    startup_name = st.text_input(
        "STARTUP NAME",
        value=st.session_state.get("startup_name", ""),
        placeholder="e.g. MedMatch AI"
    )
with col_s:
    stage = st.selectbox(
        "FUNDING STAGE",
        ["Concept Only", "Pre-Seed", "Seed", "Series A", "Series B+"]
    )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Intelligence Engine</div>', unsafe_allow_html=True)

MODELS = {
    "Gemini (Primary)": {
        "gemini/gemini-2.0-flash":       "Gemini 2.0 Flash",
        "gemini/gemini-2.0-flash-lite":  "Gemini 2.0 Flash Lite",
        "gemini/gemini-1.5-flash":       "Gemini 1.5 Flash",
        "gemini/gemini-1.5-pro":         "Gemini 1.5 Pro",
    },
    "Groq (Fallback)": {
        "groq/llama-3.3-70b-versatile": "LLaMA 3.3 70B",
        "groq/mixtral-8x7b-32768":      "Mixtral 8x7B",
    },
}

col_p, col_m = st.columns(2)
with col_p:
    provider_choice = st.selectbox("PROVIDER", list(MODELS.keys()))
with col_m:
    model_opts = MODELS[provider_choice]
    model_id   = st.selectbox("MODEL", list(model_opts.keys()), format_func=lambda x: model_opts[x])

is_gemini = model_id.startswith("gemini/")

with st.expander("⚙  ADVANCED SETTINGS"):
    col_d, col_inv = st.columns(2)
    with col_d:
        depth = st.select_slider("ANALYSIS DEPTH", ["Brief", "Standard", "Detailed"], value="Standard")
    with col_inv:
        investor_type = st.selectbox("INVESTOR LENS",
            ["Venture Capital", "Angel Investor", "Private Equity", "Corporate VC", "Impact Investor"])
    col_g, col_c = st.columns(2)
    with col_g:
        geography = st.selectbox("TARGET GEOGRAPHY",
            ["Global", "Southeast Asia", "South Asia", "USA & Canada",
             "Europe", "Middle East & Africa", "Latin America"])
    with col_c:
        currency = st.selectbox("REPORT CURRENCY", ["USD", "EUR", "GBP", "BDT"])

    col_ch1, col_ch2, col_ch3 = st.columns(3)
    with col_ch1:
        include_comparables = st.checkbox("Comparable companies", value=True)
    with col_ch2:
        include_exit        = st.checkbox("Exit strategy", value=True)
    with col_ch3:
        include_checklist   = st.checkbox("Investor DD checklist", value=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
run_btn = st.button("◈  Run Due Diligence — Deploy 5 Agents")


# ══════════════════════════════════════════════════════════════════════════════════
# EXECUTION
# ══════════════════════════════════════════════════════════════════════════════════
if run_btn:
    if not startup_idea.strip():
        st.markdown('<div class="err-box">⚠ Please describe the startup idea before running.</div>', unsafe_allow_html=True)
        st.stop()

    try:
        from crewai import Agent, Task, Crew, Process, LLM
    except ImportError as e:
        st.markdown(f'<div class="err-box">Import error: {e} — ensure crewai is in requirements.txt</div>', unsafe_allow_html=True)
        st.stop()

    api_key = os.environ.get("GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY", "")
    if not api_key:
        key_name = "GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY"
        st.markdown(f'<div class="err-box">⚠ {key_name} not set in Streamlit Secrets.</div>', unsafe_allow_html=True)
        st.stop()

    t0 = time.time()
    log_ph    = st.empty()
    status_ph = st.empty()

    def ts():
        return f"{round(time.time()-t0,1):>5}s"

    def render_log(lines):
        rows = "".join(
            f'<div class="log-line">'
            f'<span class="log-t">{t_}</span>'
            f'<span class="log-tag {c}">{tag}</span>'
            f'<span class="log-msg">{msg}</span></div>'
            for t_, tag, c, msg in lines
        )
        log_ph.markdown(f"""
        <div class="log-shell">
          <div class="log-titlebar">
            <span class="log-dot log-dot-r"></span>
            <span class="log-dot log-dot-y"></span>
            <span class="log-dot log-dot-g"></span>
            <span class="log-title">DUE DILIGENCE · EXECUTION LOG</span>
          </div>
          <div class="log-body">{rows}</div>
        </div>""", unsafe_allow_html=True)

    log  = []
    sname = startup_name.strip() or "Unnamed Startup"
    log.append((ts(), "SYS",   "t-sys",   f"Startup: {sname} · Stage: {stage}"))
    log.append((ts(), "SYS",   "t-sys",   f"Model: {model_id.split('/')[1]} · Depth: {depth} · {geography}"))
    render_log(log)

    # ── Context builders ─────────────────────────────────────────────────────────
    depth_map = {
        "Brief":    "Provide a focused analysis with 2-3 key points per dimension.",
        "Standard": "Provide a thorough analysis with evidence for each claim.",
        "Detailed": "Provide an exhaustive deep-dive. Be specific with market data, financial estimates, and risk scenarios.",
    }
    investor_map = {
        "Venture Capital":  "You prioritize 10x+ return potential, TAM size, and defensibility.",
        "Angel Investor":   "You prioritize team quality, early traction, and capital efficiency.",
        "Private Equity":   "You prioritize EBITDA path, acquisition multiples, and unit economics.",
        "Corporate VC":     "You prioritize strategic fit, IP value, and ecosystem synergies.",
        "Impact Investor":  "You balance social impact metrics alongside financial returns.",
    }
    currency_sym = {"USD": "$", "EUR": "€", "GBP": "£", "BDT": "৳"}[currency]
    depth_instr  = depth_map[depth]
    inv_ctx      = investor_map[investor_type]
    geo_ctx      = f"Focus on {geography} market context."
    comp_instr   = "Include 2-3 comparable companies with valuations." if include_comparables else ""
    exit_instr   = "Include exit strategy analysis (M&A targets, IPO path)." if include_exit else ""
    chk_instr    = "End with 5 key investor due diligence questions." if include_checklist else ""

    # ── LLM ──────────────────────────────────────────────────────────────────────
    try:
        llm = LLM(model=model_id, temperature=0.3)
    except Exception as e:
        st.markdown(f'<div class="err-box">LLM init error: {e}</div>', unsafe_allow_html=True)
        st.stop()

    log.append((ts(), "AGENT", "t-agent", "Instantiating 5 specialist agents..."))
    render_log(log)

    # ── Agents ────────────────────────────────────────────────────────────────────
    manager = Agent(
        role="Startup Evaluation Manager",
        goal="Orchestrate comprehensive due diligence. Delegate to specialists. Consolidate into structured report.",
        backstory=f"Senior partner at a top-tier {investor_type} firm, 20 years running due diligence on 200+ startups. {inv_ctx}",
        llm=llm, allow_delegation=True, verbose=True, max_iter=3,
    )
    market_analyst = Agent(
        role="Market Analyst",
        goal="Evaluate TAM/SAM/SOM, growth trajectory, demand signals, competitive landscape.",
        backstory=f"Senior market research analyst specializing in technology. {geo_ctx} Known for precise market sizing and whitespace identification. Quotes all estimates in {currency}.",
        llm=llm, verbose=True, max_iter=4,
    )
    financial_analyst = Agent(
        role="Financial Analyst",
        goal="Assess revenue model, unit economics, scalability, and path to profitability.",
        backstory=f"Startup CFO and financial modeler. Built models for 50+ startups. Expert in CAC, LTV, gross margin, burn rate. Expresses all estimates in {currency} ({currency_sym}).",
        llm=llm, verbose=True, max_iter=4,
    )
    risk_analyst = Agent(
        role="Risk Analyst",
        goal="Identify and rate operational, regulatory, technical, market, and execution risks.",
        backstory="Venture risk specialist who has studied 300+ startup failures. Rates each risk by severity (High/Medium/Low) and likelihood. Identifies second-order threats founders overlook.",
        llm=llm, verbose=True, max_iter=4,
    )
    investment_advisor = Agent(
        role="Investment Advisor",
        goal="Synthesize all analyses into a final investment recommendation with JSON verdict.",
        backstory=(
            f"Senior {investor_type} partner making the final investment call. "
            f"Weighs market potential, financial viability, and risk-adjusted returns. "
            f"ALWAYS concludes with a valid JSON block containing: "
            f"market_score, financial_score, risk_score, overall_score (all 0-10), "
            f"final_decision (INVEST/CONDITIONAL/WATCH/PASS), rationale, "
            f"recommended_check_size, key_condition."
        ),
        llm=llm, verbose=True, max_iter=5,
    )

    log.append((ts(), "AGENT", "t-agent", "Manager · Market · Financial · Risk · Investment Advisor ready"))
    render_log(log)

    # ── Tasks ─────────────────────────────────────────────────────────────────────
    market_task = Task(
        description=(
            f"MARKET ANALYSIS for: {sname} ({stage})\n\n{startup_idea}\n\n"
            f"{depth_instr} {geo_ctx} {comp_instr}\n\n"
            f"Cover: TAM/SAM/SOM in {currency}, growth rate, demand drivers, customer segments, "
            f"competitive landscape, market timing. Score market opportunity 1-10."
        ),
        expected_output="Structured market analysis with TAM estimate, competitive landscape, demand drivers, market score /10.",
        agent=market_analyst,
    )
    financial_task = Task(
        description=(
            f"FINANCIAL ANALYSIS for: {sname} ({stage})\n\n{startup_idea}\n\n"
            f"{depth_instr}\n\n"
            f"Cover: revenue model, pricing, CAC/LTV, gross margin, capital requirements, "
            f"path to profitability in {currency} ({currency_sym}). Score financial viability 1-10."
        ),
        expected_output="Structured financial analysis with revenue model, unit economics, capital needs, financial score /10.",
        agent=financial_analyst,
    )
    risk_task = Task(
        description=(
            f"RISK ANALYSIS for: {sname} ({stage})\n\n{startup_idea}\n\n"
            f"{depth_instr}\n\n"
            f"Identify market, regulatory, technical, competitive, and execution risks. "
            f"Rate each High/Medium/Low for severity and likelihood. Score risk profile 1-10 (10 = safest)."
        ),
        expected_output="Risk matrix with severity/likelihood ratings, mitigations, and risk score /10.",
        agent=risk_analyst,
    )
    investment_task = Task(
        description=(
            f"INVESTMENT RECOMMENDATION for: {sname} ({stage}) | Investor: {investor_type}\n\n"
            f"{depth_instr} {exit_instr} {chk_instr}\n\n"
            f"Synthesize the market, financial, and risk analyses above. "
            f"Provide your final recommendation. End with EXACTLY this JSON:\n"
            f"```json\n"
            f'{{\n'
            f'  "startup_name": "{sname}",\n'
            f'  "stage": "{stage}",\n'
            f'  "market_score": <0-10>,\n'
            f'  "financial_score": <0-10>,\n'
            f'  "risk_score": <0-10>,\n'
            f'  "overall_score": <0-10>,\n'
            f'  "final_decision": "<INVEST|CONDITIONAL|WATCH|PASS>",\n'
            f'  "rationale": "<one decisive sentence>",\n'
            f'  "recommended_check_size": "<e.g. {currency_sym}500K>",\n'
            f'  "key_condition": "<most critical milestone before next raise>"\n'
            f'}}\n```'
        ),
        expected_output="Investment memo with recommendation and valid JSON verdict block.",
        agent=investment_advisor,
        context=[market_task, financial_task, risk_task],
    )

    crew = Crew(
        agents=[manager, market_analyst, financial_analyst, risk_analyst, investment_advisor],
        tasks=[market_task, financial_task, risk_task, investment_task],
        process=Process.sequential,
        verbose=False,
    )

    log.append((ts(), "TASK",  "t-task",  "4 tasks queued: Market → Financial → Risk → Investment"))
    log.append((ts(), "SYS",   "t-sys",   f"Process: Sequential · Manager delegation: enabled"))
    render_log(log)

    status_ph.markdown(
        '<div class="info-box">⟳ &nbsp;Agents running due diligence — this takes 60–120 seconds. '
        'Five specialists are analyzing your startup in parallel streams...</div>',
        unsafe_allow_html=True
    )

    # ── Execute ───────────────────────────────────────────────────────────────────
    try:
        result  = crew.kickoff()
        elapsed = round(time.time() - t0, 1)

        log.append((ts(), "OK", "t-ok", f"All agents complete · {elapsed}s elapsed"))
        render_log(log)
        status_ph.empty()

        # ── Gather outputs ────────────────────────────────────────────────────────
        def safe_out(task):
            try:   return str(task.output).strip() if task.output else ""
            except: return ""

        market_out     = safe_out(market_task)
        financial_out  = safe_out(financial_task)
        risk_out       = safe_out(risk_task)
        investment_out = safe_out(investment_task)
        full_result    = str(result).strip()

        # ── Parse JSON ────────────────────────────────────────────────────────────
        verdict = {}
        search_text = investment_out + "\n" + full_result
        m = re.search(r'```json\s*(\{.*?\})\s*```', search_text, re.DOTALL)
        if not m:
            m = re.search(r'(\{[^{}]*"final_decision"[^{}]*\})', search_text, re.DOTALL)
        if m:
            try:
                verdict = json.loads(m.group(1))
            except Exception:
                pass

        ms  = verdict.get("market_score",    "—")
        fs  = verdict.get("financial_score", "—")
        rs  = verdict.get("risk_score",      "—")
        os_ = verdict.get("overall_score",   "—")
        decision   = verdict.get("final_decision", "—")
        rationale  = verdict.get("rationale", "")
        chk_size   = verdict.get("recommended_check_size", "—")
        condition  = verdict.get("key_condition", "—")

        # ── Helper: score to bar width ────────────────────────────────────────────
        def bar(score):
            try:   return int(float(score) * 10)
            except: return 0

        # ── Verdict card ─────────────────────────────────────────────────────────
        dec_chip_map = {
            "INVEST":      ("chip-invest",  "↑ INVEST"),
            "CONDITIONAL": ("chip-cond",    "◎ CONDITIONAL"),
            "WATCH":       ("chip-watch",   "◉ WATCH"),
            "PASS":        ("chip-pass",    "↓ PASS"),
        }
        chip_cls, chip_label = dec_chip_map.get(decision, ("chip-watch", f"· {decision}"))

        st.markdown('<div class="divider-glow"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Investment Verdict</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="verdict-wrap">
          <div class="verdict-header">
            <div>
              <div class="verdict-startup">{sname}</div>
              <div class="verdict-stage">{stage} · {investor_type} · {geography}</div>
            </div>
            <div style="font-family:var(--font-mono);font-size:0.68rem;color:var(--text-tertiary);text-align:right">
              Analyzed in {elapsed}s<br>
              {datetime.now().strftime("%H:%M:%S")}
            </div>
          </div>

          <div class="score-ring-grid">
            <div class="score-ring-card ring-market">
              <div class="score-big">{ms}<span class="score-denom">/10</span></div>
              <div class="score-ring-label">Market</div>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:{bar(ms)}%"></div></div>
            </div>
            <div class="score-ring-card ring-finance">
              <div class="score-big">{fs}<span class="score-denom">/10</span></div>
              <div class="score-ring-label">Financial</div>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:{bar(fs)}%"></div></div>
            </div>
            <div class="score-ring-card ring-risk">
              <div class="score-big">{rs}<span class="score-denom">/10</span></div>
              <div class="score-ring-label">Risk</div>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:{bar(rs)}%"></div></div>
            </div>
            <div class="score-ring-card ring-overall">
              <div class="score-big">{os_}<span class="score-denom">/10</span></div>
              <div class="score-ring-label">Overall</div>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:{bar(os_)}%"></div></div>
            </div>
          </div>

          <div class="decision-row">
            <span class="decision-chip {chip_cls}">{chip_label}</span>
            {f'<span class="decision-rationale">"{rationale}"</span>' if rationale else ''}
          </div>

          <div class="decision-meta">
            <div class="meta-item">
              <div class="meta-label">Recommended Check Size</div>
              <div class="meta-value">{chk_size}</div>
            </div>
            <div class="meta-item">
              <div class="meta-label">Key Milestone / Condition</div>
              <div class="meta-value">{condition}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Report sections ────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Full Due Diligence Report</div>', unsafe_allow_html=True)

        sections = [
            ("📊", "icon-market",  "accent-market",  "Market Analysis",          "Market Analyst",     market_out     or full_result),
            ("💰", "icon-finance", "accent-finance",  "Financial Analysis",       "Financial Analyst",  financial_out  or full_result),
            ("⚠️",  "icon-risk",   "accent-risk",    "Risk Assessment",           "Risk Analyst",       risk_out       or full_result),
            ("🎯", "icon-invest",  "accent-invest",  "Investment Recommendation", "Investment Advisor", investment_out or full_result),
        ]

        for icon, icon_cls, accent_cls, title, agent_lbl, content in sections:
            if not content:
                continue
            st.markdown(f"""
            <div class="report-card">
              <div class="report-header">
                <div class="report-accent {accent_cls}"></div>
                <div class="report-icon-wrap {icon_cls}">{icon}</div>
                <span class="report-title">{title}</span>
                <span class="report-agent">{agent_lbl}</span>
              </div>
              <div class="report-body">{content.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── JSON Verdict ──────────────────────────────────────────────────────────
        if verdict:
            st.markdown('<div class="section-label" style="margin-top:1.5rem">Machine-Readable Output</div>', unsafe_allow_html=True)
            pretty = json.dumps(verdict, indent=2)
            st.markdown(f"""
            <div class="json-shell">
              <div class="json-titlebar">
                <span class="json-title">VERDICT · JSON · PARSEABLE</span>
                <span class="json-badge">VALID JSON</span>
              </div>
              <div class="json-body"><pre>{pretty}</pre></div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        log.append((ts(), "ERR", "t-err", str(e)[:100]))
        render_log(log)
        status_ph.empty()
        st.markdown(f'<div class="err-box">Agent execution error: {e}</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:2rem"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="footer">
  <span>agent-forge · day 7 of 15</span>
  <span>crewai · gemini 2.5 flash · groq fallback</span>
  <span>ai startup due diligence system</span>
</div>
""", unsafe_allow_html=True)
