import streamlit as st
import os
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CrewAI Market Research",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Minimal CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0d0d0d;
    color: #e8e8e8;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 2rem 4rem 2rem; max-width: 780px; }

/* Header */
.app-header {
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
}
.app-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.15rem;
    font-weight: 600;
    color: #00ff9d;
    letter-spacing: 0.05em;
    margin: 0;
}
.app-sub {
    font-size: 0.78rem;
    color: #555;
    margin-top: 0.3rem;
    font-family: 'IBM Plex Mono', monospace;
}

/* Labels */
.field-label {
    font-size: 0.72rem;
    font-family: 'IBM Plex Mono', monospace;
    color: #666;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    display: block;
}

/* Input overrides */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
    color: #e8e8e8 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #00ff9d !important;
    box-shadow: 0 0 0 1px #00ff9d22 !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: #141414 !important;
    color: #e8e8e8 !important;
}

/* Button */
.stButton > button {
    background: #00ff9d !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    padding: 0.6rem 1.6rem !important;
    cursor: pointer !important;
    transition: opacity 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
.stButton > button:disabled { opacity: 0.4 !important; }

/* Status chip */
.status-running {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #f0b429;
    border: 1px solid #f0b42944;
    border-radius: 3px;
    padding: 0.2rem 0.6rem;
    margin-bottom: 1rem;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* Result box */
.result-box {
    background: #111;
    border: 1px solid #222;
    border-left: 3px solid #00ff9d;
    border-radius: 4px;
    padding: 1.4rem 1.6rem;
    font-size: 0.88rem;
    line-height: 1.75;
    white-space: pre-wrap;
    font-family: 'IBM Plex Sans', sans-serif;
    color: #d4d4d4;
    margin-top: 1.2rem;
}
.result-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #00ff9d;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* Error box */
.error-box {
    background: #1a0a0a;
    border: 1px solid #ff444444;
    border-left: 3px solid #ff4444;
    border-radius: 4px;
    padding: 1rem 1.4rem;
    font-size: 0.82rem;
    font-family: 'IBM Plex Mono', monospace;
    color: #ff8888;
    margin-top: 1rem;
}

/* Divider */
.thin-divider {
    border: none;
    border-top: 1px solid #1e1e1e;
    margin: 1.8rem 0;
}

/* Key expander */
.stExpander {
    border: 1px solid #1e1e1e !important;
    border-radius: 4px !important;
    background: #0d0d0d !important;
}

/* Spinner override */
.stSpinner > div { border-top-color: #00ff9d !important; }
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <p class="app-title">⬡ CREWAI MARKET RESEARCH</p>
    <p class="app-sub">Day 1 Assignment · Powered by Groq + LLaMA 3.3 70B</p>
</div>
""", unsafe_allow_html=True)


# ── API Key — from Streamlit Secrets only (never shown in UI) ──────────────────
try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass  # Key must be set in Streamlit Cloud → Settings → Secrets

st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)


# ── Form ───────────────────────────────────────────────────────────────────────
PRESETS = {
    "AI Fitness App": {
        "idea": "An AI-powered personalized fitness app targeting busy professionals aged 25–40",
        "role": "Senior Market Research Analyst",
        "goal": "Analyze market size, target audience, top competitors, and 3 key growth opportunities for the fitness tech space.",
        "backstory": "You are a Senior Market Research Analyst with 10+ years in health & fitness tech. You've worked with Strava, Noom, and MyFitnessPal. Known for data-driven, structured market insights.",
    },
    "AI YouTube Script Generator": {
        "idea": "An AI SaaS tool that generates SEO-optimized YouTube scripts for content creators in minutes",
        "role": "Digital Content Market Strategist",
        "goal": "Identify creator economy TAM, ideal customer profile, pricing strategy, and 90-day go-to-market plan.",
        "backstory": "You are a Digital Content Market Strategist with 8 years at the intersection of SaaS and creator economy. You've advised 50+ content startups. You think in TAM, ARR, and viral growth loops.",
    },
    "AI Real Estate Analyzer": {
        "idea": "An AI tool that helps property investors evaluate real estate deals, predict rental yields, and spot undervalued markets",
        "role": "PropTech Investment Research Analyst",
        "goal": "Assess TAM/SAM/SOM, user segments, revenue models, and provide an investment attractiveness score with final recommendation.",
        "backstory": "You are a PropTech Investment Analyst with 12 years at Zillow, Redfin, and a VC firm focused on PropTech. You turn complex market data into clear investment decisions.",
    },
    "Custom Idea": {
        "idea": "",
        "role": "",
        "goal": "",
        "backstory": "",
    },
}

MODELS = {
    "llama-3.3-70b-versatile (Recommended)": "groq/llama-3.3-70b-versatile",
    "llama-3.1-8b-instant (Fastest)": "groq/llama-3.1-8b-instant",
    "mixtral-8x7b-32768 (Balanced)": "groq/mixtral-8x7b-32768",
}

col1, col2 = st.columns([3, 2])
with col1:
    st.markdown('<span class="field-label">Business Idea Preset</span>', unsafe_allow_html=True)
    preset_choice = st.selectbox("Preset", list(PRESETS.keys()), label_visibility="collapsed")

with col2:
    st.markdown('<span class="field-label">Groq Model</span>', unsafe_allow_html=True)
    model_choice = st.selectbox("Model", list(MODELS.keys()), label_visibility="collapsed")

p = PRESETS[preset_choice]

st.markdown('<span class="field-label">Business Idea Description</span>', unsafe_allow_html=True)
business_idea = st.text_area(
    "Business Idea",
    value=p["idea"],
    height=80,
    placeholder="Describe the business idea to research...",
    label_visibility="collapsed",
)

with st.expander("⚙️ Customize Agent (optional)"):
    agent_role = st.text_input("Agent Role", value=p["role"], placeholder="e.g. Senior Market Research Analyst")
    agent_goal = st.text_area("Agent Goal", value=p["goal"], height=90, placeholder="What should the agent optimize for?")
    agent_backstory = st.text_area("Agent Backstory", value=p["backstory"], height=90, placeholder="Expertise, experience, personality...")

    st.markdown('<span class="field-label">Output Sections (one per line)</span>', unsafe_allow_html=True)
    default_sections = "1. Market Overview (size + growth)\n2. Target Audience Profile\n3. Top 3 Competitors\n4. Key Opportunities (3 points)\n5. Recommendation"
    output_format = st.text_area("Output Format", value=default_sections, height=120, label_visibility="collapsed")

st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)

run_btn = st.button("▶  RUN RESEARCH")


# ── Execution ──────────────────────────────────────────────────────────────────
if run_btn:
    if not business_idea.strip():
        st.markdown('<div class="error-box">⚠ Please enter a business idea description.</div>', unsafe_allow_html=True)
        st.stop()

    # Lazy import so app loads fast before packages are installed
    try:
        from crewai import Agent, Task, Crew, LLM
    except ImportError:
        st.markdown('<div class="error-box">crewai not installed. Run:  pip install crewai</div>', unsafe_allow_html=True)
        st.stop()

    # Set ALL required env vars before any crewai/litellm call
    groq_api_key = os.environ.get("GROQ_API_KEY", "")
    os.environ["GROQ_API_KEY"] = groq_api_key
    os.environ["OPENAI_API_KEY"] = "dummy-not-used"   # CrewAI still checks for this

    model_id = MODELS[model_choice]
    role = agent_role.strip() or "Senior Market Research Analyst"
    goal = agent_goal.strip() or f"Analyze the market potential for: {business_idea[:120]}"
    backstory = agent_backstory.strip() or (
        "You are an experienced Market Research Analyst with 10+ years of expertise "
        "across multiple industries. You deliver clear, structured, data-driven insights."
    )
    sections = output_format.strip() or default_sections

    status_placeholder = st.empty()
    result_placeholder = st.empty()

    status_placeholder.markdown(
        '<div class="status-running">● AGENT RUNNING…</div>', unsafe_allow_html=True
    )

    t_start = time.time()

    try:
        llm = LLM(
            model=model_id,
            api_key=groq_api_key,
            temperature=0.7,
        )

        researcher = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=False,   # keep Streamlit console clean
        )

        task = Task(
            description=(
                f"Conduct a comprehensive market research analysis for the following business idea:\n\n"
                f"'{business_idea}'\n\n"
                f"Be specific, use real market data where possible, and think like a professional analyst."
            ),
            expected_output=(
                f"A well-structured market research report with these sections:\n{sections}"
            ),
            agent=researcher,
        )

        crew = Crew(
            agents=[researcher],
            tasks=[task],
            verbose=False,
        )

        result = crew.kickoff()
        elapsed = round(time.time() - t_start, 1)

        status_placeholder.empty()
        result_placeholder.markdown(
            f'<div class="result-header">▸ RESEARCH COMPLETE — {elapsed}s · {model_id.split("/")[1]}</div>'
            f'<div class="result-box">{str(result)}</div>',
            unsafe_allow_html=True,
        )

    except Exception as e:
        status_placeholder.empty()
        result_placeholder.markdown(
            f'<div class="error-box">✗ Error: {str(e)}</div>',
            unsafe_allow_html=True,
        )
