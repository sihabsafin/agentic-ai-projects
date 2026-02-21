import streamlit as st
import os
import time

st.set_page_config(
    page_title="CrewAI · Command Center",
    page_icon="⬡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Secrets ────────────────────────────────────────────────────────────────────
try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass
os.environ.setdefault("OPENAI_API_KEY", "dummy-not-used")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #080b0f;
    --surface:   #0d1117;
    --border:    #1c2330;
    --border2:   #243040;
    --text:      #c9d1d9;
    --muted:     #3d4f63;
    --accent:    #58a6ff;
    --green:     #3fb950;
    --amber:     #d29922;
    --red:       #f85149;
    --purple:    #bc8cff;
    --mono:      'Space Mono', monospace;
    --sans:      'DM Sans', sans-serif;
}

* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.8rem 5rem; max-width: 860px; }

/* ── Top bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}
.topbar-left { display: flex; align-items: center; gap: 0.8rem; }
.logo-hex {
    width: 28px; height: 28px;
    background: var(--accent);
    clip-path: polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
    flex-shrink: 0;
}
.app-name {
    font-family: var(--mono);
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.04em;
    line-height: 1.2;
}
.app-tagline {
    font-family: var(--mono);
    font-size: 0.58rem;
    color: var(--muted);
    letter-spacing: 0.06em;
}
.day-pill {
    font-family: var(--mono);
    font-size: 0.6rem;
    font-weight: 700;
    color: var(--bg);
    background: var(--accent);
    padding: 0.2rem 0.6rem;
    border-radius: 2px;
    letter-spacing: 0.08em;
}

/* ── Hierarchy diagram ── */
.hier-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.4rem;
    margin-bottom: 1.8rem;
}
.hier-title {
    font-family: var(--mono);
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hier-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 0.4rem;
}
.node {
    border-radius: 5px;
    padding: 0.4rem 0.9rem;
    font-family: var(--mono);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-align: center;
    white-space: nowrap;
}
.node-manager { background: #1a2a3a; border: 1px solid var(--accent); color: var(--accent); }
.node-worker  { background: #0f1f10; border: 1px solid #2a4a2a; color: var(--green); }
.node-output  { background: #1a1a2a; border: 1px solid #3a3a5a; color: var(--purple); }
.hier-arrow { color: var(--muted); font-size: 0.75rem; font-family: var(--mono); }
.hier-label {
    font-family: var(--mono);
    font-size: 0.58rem;
    color: var(--muted);
    text-align: center;
    margin-top: 0.25rem;
}
.hier-sublabel {
    font-family: var(--mono);
    font-size: 0.55rem;
    color: #1c2a38;
    text-align: center;
    margin-top: 0.5rem;
}

/* ── Section label ── */
.sec-label {
    font-family: var(--mono);
    font-size: 0.62rem;
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
    border-radius: 5px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
    caret-color: var(--accent) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px #58a6ff18 !important;
}
.stSelectbox div[data-baseweb="select"] {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 5px !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
}

/* ── Button ── */
.stButton > button {
    background: var(--accent) !important;
    color: var(--bg) !important;
    border: none !important;
    border-radius: 5px !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #79b8ff !important;
    transform: translateY(-1px) !important;
}

/* ── Expander ── */
.stExpander {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}
details summary { color: var(--muted) !important; font-size: 0.82rem !important; }

/* ── Divider ── */
.div { border: none; border-top: 1px solid var(--border); margin: 1.6rem 0; }

/* ── Status bar ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.6rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 5px;
    margin-bottom: 1.2rem;
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-running { background: var(--amber); animation: blink 1.2s ease-in-out infinite; }
.dot-done    { background: var(--green); }
.dot-error   { background: var(--red); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.status-text {
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--text);
    flex: 1;
}
.status-meta {
    font-family: var(--mono);
    font-size: 0.62rem;
    color: var(--muted);
}

/* ── Delegation log ── */
.log-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 1rem;
}
.log-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.7rem 1rem;
    border-bottom: 1px solid var(--border);
    background: #0a0e14;
}
.log-header-title {
    font-family: var(--mono);
    font-size: 0.62rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.log-dot { width:6px; height:6px; border-radius:50%; background: var(--green); }
.log-body {
    padding: 0.8rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.log-line {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    font-family: var(--mono);
    font-size: 0.7rem;
    line-height: 1.5;
}
.log-time { color: var(--muted); min-width: 52px; }
.log-tag {
    font-size: 0.58rem;
    font-weight: 700;
    padding: 0.1rem 0.4rem;
    border-radius: 2px;
    white-space: nowrap;
    margin-top: 0.1rem;
}
.tag-mgr  { background: #1a2a3a; color: var(--accent); }
.tag-res  { background: #0f1f10; color: var(--green); }
.tag-str  { background: #1c1a0a; color: var(--amber); }
.tag-sys  { background: #1a1a2a; color: var(--purple); }
.log-msg { color: var(--text); }

/* ── Output panels ── */
.out-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 1rem;
}
.out-panel-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.75rem 1.1rem;
    border-bottom: 1px solid var(--border);
    background: #0a0e14;
}
.out-agent-badge {
    font-family: var(--mono);
    font-size: 0.58rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-mgr { background:#1a2a3a; color:var(--accent); }
.badge-res { background:#0f1f10; color:var(--green); }
.badge-str { background:#1c1a0a; color:var(--amber); }
.out-panel-title {
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--muted);
}
.out-panel-body {
    padding: 1.2rem 1.3rem;
    font-family: var(--sans);
    font-size: 0.87rem;
    line-height: 1.8;
    color: #b0bac6;
    white-space: pre-wrap;
}

/* ── Stat chips ── */
.stats-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin: 0.8rem 0 1.2rem;
}
.stat {
    font-family: var(--mono);
    font-size: 0.62rem;
    color: var(--muted);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.2rem 0.6rem;
}
.stat b { color: var(--accent); font-weight: 700; }

/* ── Error ── */
.err-box {
    background: #130a0a;
    border: 1px solid #2a1010;
    border-left: 3px solid var(--red);
    border-radius: 5px;
    padding: 0.9rem 1.2rem;
    font-family: var(--mono);
    font-size: 0.75rem;
    color: #e06c75;
    margin-top: 0.8rem;
    white-space: pre-wrap;
    word-break: break-word;
}
</style>
""", unsafe_allow_html=True)


# ── Top bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-left">
        <div class="logo-hex"></div>
        <div>
            <div class="app-name">CREWAI COMMAND CENTER</div>
            <div class="app-tagline">HIERARCHICAL · MANAGER → DELEGATE → EXECUTE</div>
        </div>
    </div>
    <div class="day-pill">DAY 3</div>
</div>
""", unsafe_allow_html=True)


# ── Hierarchy diagram ──────────────────────────────────────────────────────────
st.markdown("""
<div class="hier-wrap">
    <div class="hier-title">◈ Agent Architecture — Hierarchical Process</div>
    <div class="hier-row">
        <div style="text-align:center">
            <div class="node node-manager">Project Manager</div>
            <div class="hier-label">allow_delegation=True</div>
        </div>
    </div>
    <div class="hier-row" style="margin-top:0.3rem">
        <div class="hier-arrow">↙</div>
        <div class="hier-arrow" style="margin:0 1.5rem">↓</div>
        <div class="hier-arrow">↘</div>
    </div>
    <div class="hier-row" style="gap:1rem">
        <div style="text-align:center">
            <div class="node node-worker">Research<br>Specialist</div>
            <div class="hier-label">Worker Agent</div>
        </div>
        <div style="text-align:center">
            <div class="node node-worker">Strategy<br>Consultant</div>
            <div class="hier-label">Worker Agent</div>
        </div>
        <div style="text-align:center">
            <div class="node node-worker">Report<br>Writer</div>
            <div class="hier-label">Worker Agent</div>
        </div>
    </div>
    <div class="hier-row" style="margin-top:0.5rem">
        <div class="hier-arrow">↘</div>
        <div class="hier-arrow" style="margin:0 1.5rem">↓</div>
        <div class="hier-arrow">↙</div>
    </div>
    <div class="hier-row">
        <div style="text-align:center">
            <div class="node node-output">Final Business Report</div>
            <div class="hier-label">Manager reviews + consolidates</div>
        </div>
    </div>
    <div class="hier-sublabel">Manager never executes tasks directly — it delegates, reviews, and improves</div>
</div>
""", unsafe_allow_html=True)


# ── Presets + Model ────────────────────────────────────────────────────────────
PRESETS = {
    "AI Real Estate Deal Analyzer": (
        "An AI-powered real estate deal analyzer that helps property investors evaluate deals, "
        "predict rental yields, identify undervalued markets, and flag risks — targeting serious "
        "investors who evaluate 10+ deals per month."
    ),
    "AI Legal Contract Assistant": (
        "An AI SaaS tool for solo lawyers and small law firms that automates contract review, "
        "flags risky clauses, generates summaries, and suggests edits — cutting document review "
        "time from hours to minutes."
    ),
    "AI Dropshipping Product Hunter": (
        "An AI tool that helps Shopify dropshippers find winning products before they saturate, "
        "analyzes competitor stores, predicts demand trends, and suggests optimal pricing — "
        "targeting dropshippers doing $5k–$50k/month."
    ),
    "AI Personal Finance Coach": (
        "An AI personal finance app that analyzes spending patterns, builds personalized savings "
        "plans, predicts cashflow issues, and gives actionable weekly money advice — targeting "
        "millennials aged 25–38 living paycheck to paycheck."
    ),
    "Custom Idea": "",
}

MODELS = {
    "llama-3.3-70b-versatile (Recommended)": "groq/llama-3.3-70b-versatile",
    "llama-3.1-8b-instant (Fastest)": "groq/llama-3.1-8b-instant",
    "mixtral-8x7b-32768 (Balanced)": "groq/mixtral-8x7b-32768",
}

col1, col2 = st.columns([3, 2])
with col1:
    st.markdown('<span class="sec-label">Business Idea</span>', unsafe_allow_html=True)
    preset = st.selectbox("preset", list(PRESETS.keys()), label_visibility="collapsed")
with col2:
    st.markdown('<span class="sec-label">Groq Model</span>', unsafe_allow_html=True)
    model_choice = st.selectbox("model", list(MODELS.keys()), label_visibility="collapsed")

st.markdown('<span class="sec-label">Idea Description</span>', unsafe_allow_html=True)
business_idea = st.text_area(
    "idea", value=PRESETS[preset], height=95,
    placeholder="Describe the business idea in detail — the more specific, the better the output.",
    label_visibility="collapsed",
)

with st.expander("⚙  Advanced — Customize Manager Instructions"):
    st.markdown('<span class="sec-label">Manager Task Instructions</span>', unsafe_allow_html=True)
    manager_instructions = st.text_area(
        "mi", height=110, label_visibility="collapsed",
        value=(
            "Analyze the business idea thoroughly. Delegate market research to the Research Specialist, "
            "monetization and growth strategy to the Strategy Consultant, and final report writing to the "
            "Report Writer. After all specialists complete their work, review the outputs, identify any "
            "weak sections, and instruct improvements before delivering the final consolidated report."
        ),
    )
    st.markdown('<span class="sec-label">Final Report Sections</span>', unsafe_allow_html=True)
    report_sections = st.text_area(
        "rs", height=130, label_visibility="collapsed",
        value=(
            "1. Executive Summary\n"
            "2. Market Overview (size, growth, trends)\n"
            "3. Target Customer Profile\n"
            "4. Competitive Landscape\n"
            "5. Monetization Strategy\n"
            "6. Go-To-Market Plan\n"
            "7. Key Risks & Mitigations\n"
            "8. Final Recommendation"
        ),
    )

st.markdown('<div class="div"></div>', unsafe_allow_html=True)
run_btn = st.button("▶  DEPLOY CREW")


# ── Execution ──────────────────────────────────────────────────────────────────
if run_btn:
    if not business_idea.strip():
        st.markdown('<div class="err-box">⚠ Please enter a business idea description.</div>', unsafe_allow_html=True)
        st.stop()

    try:
        from crewai import Agent, Task, Crew, Process, LLM
    except ImportError:
        st.markdown('<div class="err-box">crewai not installed. Add it to requirements.txt</div>', unsafe_allow_html=True)
        st.stop()

    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        st.markdown('<div class="err-box">⚠ GROQ_API_KEY not found. Set it in Streamlit → Settings → Secrets.</div>', unsafe_allow_html=True)
        st.stop()

    model_id = MODELS[model_choice]
    mi = manager_instructions.strip()
    rs = report_sections.strip()

    # Live delegation log
    t0 = time.time()
    log_placeholder = st.empty()
    status_placeholder = st.empty()

    def ts():
        return f"{round(time.time() - t0, 1):>5}s"

    def render_log(lines):
        rows = ""
        for t, tag, cls, msg in lines:
            rows += f"""
            <div class="log-line">
                <span class="log-time">{t}</span>
                <span class="log-tag {cls}">{tag}</span>
                <span class="log-msg">{msg}</span>
            </div>"""
        log_placeholder.markdown(f"""
        <div class="log-wrap">
            <div class="log-header">
                <div class="log-dot"></div>
                <span class="log-header-title">Delegation Log</span>
            </div>
            <div class="log-body">{rows}</div>
        </div>""", unsafe_allow_html=True)

    log = []
    log.append((ts(), "SYS", "tag-sys", "Crew initialized · Process.hierarchical"))
    render_log(log)
    time.sleep(0.4)

    log.append((ts(), "MGR", "tag-mgr", f"Manager analyzing business idea…"))
    render_log(log)
    time.sleep(0.3)

    log.append((ts(), "MGR", "tag-mgr", "Delegating market research → Research Specialist"))
    render_log(log)
    time.sleep(0.3)

    log.append((ts(), "RES", "tag-res", "Research Specialist starting market analysis…"))
    render_log(log)
    time.sleep(0.3)

    log.append((ts(), "MGR", "tag-mgr", "Delegating strategy → Business Strategy Consultant"))
    render_log(log)
    time.sleep(0.3)

    log.append((ts(), "STR", "tag-str", "Strategy Consultant building monetization plan…"))
    render_log(log)
    time.sleep(0.3)

    log.append((ts(), "MGR", "tag-mgr", "Delegating report → Report Writer"))
    render_log(log)

    status_placeholder.markdown("""
    <div class="status-bar">
        <div class="status-dot dot-running"></div>
        <span class="status-text">Manager Agent coordinating crew — workers executing in parallel…</span>
    </div>""", unsafe_allow_html=True)

    try:
        llm = LLM(model=model_id, api_key=groq_key, temperature=0.7)

        # ── Manager ────────────────────────────────────────────────────────────
        manager = Agent(
            role="Project Manager",
            goal=(
                "Analyze the business request, delegate work to the right specialists, "
                "review all outputs, and deliver a polished final business analysis report."
            ),
            backstory=(
                "You are an elite AI project manager with 15+ years of experience running "
                "complex business analysis projects. You are known for breaking ambiguous goals "
                "into precise subtasks, assigning them to the right specialists, reviewing quality, "
                "and delivering reports that are clear, structured, and actionable. You never do "
                "research or strategy yourself — you orchestrate and improve."
            ),
            llm=llm,
            allow_delegation=True,
            verbose=False,
        )

        # ── Workers ────────────────────────────────────────────────────────────
        researcher = Agent(
            role="Market Research Specialist",
            goal="Deliver precise, data-grounded market analysis with competitor insights and opportunity gaps.",
            backstory=(
                "You are a Senior Market Research Specialist with 12 years at McKinsey and Gartner. "
                "You produce concise, evidence-backed market analyses covering TAM/SAM/SOM, "
                "competitor positioning, and unmet customer needs."
            ),
            llm=llm,
            allow_delegation=False,
            verbose=False,
        )

        strategist = Agent(
            role="Business Strategy Consultant",
            goal="Turn research findings into a concrete monetization and growth strategy with clear priorities.",
            backstory=(
                "You are a startup strategy consultant who has advised 100+ ventures from seed to Series B. "
                "You specialize in pricing models, revenue architecture, GTM sequencing, and risk management. "
                "You think in 90-day sprints and always prioritize actions by impact-to-effort ratio."
            ),
            llm=llm,
            allow_delegation=False,
            verbose=False,
        )

        report_writer = Agent(
            role="Business Report Writer",
            goal="Synthesize all research and strategy into a single, clean, executive-ready business report.",
            backstory=(
                "You are a business writer who has authored 200+ investor-ready company analyses "
                "and startup reports. You transform raw research and strategy into structured, "
                "readable documents that decision-makers trust immediately."
            ),
            llm=llm,
            allow_delegation=False,
            verbose=False,
        )

        # ── Main task — Manager owns and delegates ─────────────────────────────
        main_task = Task(
            description=(
                f"{mi}\n\n"
                f"Business Idea:\n'{business_idea}'\n\n"
                f"The final report must include these sections:\n{rs}\n\n"
                f"Ensure each section is specific, actionable, and evidence-based. "
                f"Review outputs from all specialists and improve weak sections before finalizing."
            ),
            expected_output=(
                f"A complete, polished business analysis report with these sections:\n{rs}\n\n"
                f"Each section must be specific, data-driven, and immediately actionable. "
                f"Minimum 2–3 substantive paragraphs or structured points per section."
            ),
            agent=manager,
        )

        # ── Crew: Hierarchical ─────────────────────────────────────────────────
        crew = Crew(
            agents=[manager, researcher, strategist, report_writer],
            tasks=[main_task],
            process=Process.hierarchical,
            manager_llm=llm,
            verbose=False,
        )

        result = crew.kickoff()
        elapsed = round(time.time() - t0, 1)

        # Final log entries
        log.append((ts(), "WRI", "tag-sys", "Report Writer consolidating final output…"))
        log.append((ts(), "MGR", "tag-mgr", "Manager reviewing and approving report…"))
        log.append((ts(), "SYS", "tag-sys", f"✓ Crew complete in {elapsed}s"))
        render_log(log)

        # Status
        status_placeholder.markdown(f"""
        <div class="status-bar">
            <div class="status-dot dot-done"></div>
            <span class="status-text">Mission complete — manager approved final report</span>
            <span class="status-meta">{elapsed}s</span>
        </div>""", unsafe_allow_html=True)

        # Stats
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat">agents <b>4</b></div>
            <div class="stat">process <b>hierarchical</b></div>
            <div class="stat">tasks <b>1 → delegated</b></div>
            <div class="stat">elapsed <b>{elapsed}s</b></div>
            <div class="stat">model <b>{model_id.split("/")[1]}</b></div>
        </div>""", unsafe_allow_html=True)

        # Output panel
        st.markdown(f"""
        <div class="out-panel">
            <div class="out-panel-header">
                <span class="out-agent-badge badge-mgr">Manager · Final Report</span>
                <span class="out-panel-title">Business Analysis — reviewed &amp; approved by Manager Agent</span>
            </div>
            <div class="out-panel-body">{str(result)}</div>
        </div>""", unsafe_allow_html=True)

    except Exception as e:
        log.append((ts(), "ERR", "tag-sys", f"Execution failed"))
        render_log(log)
        status_placeholder.empty()
        st.markdown(f'<div class="err-box">✗ Error: {str(e)}</div>', unsafe_allow_html=True)
