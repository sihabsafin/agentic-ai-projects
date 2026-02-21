import streamlit as st
import os
import time
import requests

st.set_page_config(
    page_title="AgentForge · Live Data Intelligence",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Secrets ────────────────────────────────────────────────────────────────────
for secret_key in ["GEMINI_API_KEY", "GROQ_API_KEY"]:
    try:
        os.environ[secret_key] = st.secrets[secret_key]
    except Exception:
        pass
if os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GEMINI_API_KEY"]
os.environ.setdefault("OPENAI_API_KEY", "dummy-not-used")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

:root {
    --bg:        #f7f6f3;
    --surface:   #ffffff;
    --surface2:  #f0ede8;
    --border:    #e4dfd8;
    --border2:   #cfc9c0;
    --text:      #1a1714;
    --muted:     #8c8278;
    --accent:    #1a56db;
    --accent2:   #e8f0fe;
    --green:     #0a7c3e;
    --green-bg:  #e8f5ed;
    --amber:     #b45309;
    --amber-bg:  #fef3e2;
    --red:       #c0392b;
    --red-bg:    #fdecea;
    --purple:    #6d28d9;
    --purple-bg: #ede9fe;
    --mono:      'Fira Code', monospace;
    --sans:      'Outfit', sans-serif;
    --shadow:    0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
}

* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.8rem 5rem; max-width: 880px; }

/* ── Topbar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 2rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: center; gap: 0.7rem; }
.brand-icon {
    width: 32px; height: 32px;
    background: var(--accent);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; color: white;
    font-weight: 700;
}
.brand-name {
    font-size: 1rem; font-weight: 700;
    color: var(--text); letter-spacing: -0.01em;
}
.brand-tagline {
    font-size: 0.72rem; color: var(--muted);
    font-family: var(--mono); margin-top: 1px;
}
.topbar-right { display: flex; align-items: center; gap: 0.6rem; }
.day-pill {
    font-family: var(--mono); font-size: 0.6rem; font-weight: 600;
    color: var(--accent); background: var(--accent2);
    border: 1px solid #c5d9f9;
    padding: 0.2rem 0.6rem; border-radius: 20px;
}
.live-pill {
    display: flex; align-items: center; gap: 0.35rem;
    font-family: var(--mono); font-size: 0.6rem; font-weight: 600;
    color: var(--green); background: var(--green-bg);
    border: 1px solid #b2dfca;
    padding: 0.2rem 0.7rem; border-radius: 20px;
}
.live-dot { width:5px; height:5px; border-radius:50%; background:var(--green); animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.8)} }

/* ── Section heading ── */
.sec-heading {
    font-size: 0.65rem; font-weight: 600; color: var(--muted);
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 0.5rem; display: block;
    font-family: var(--mono);
}

/* ── Mode cards ── */
.mode-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; margin-bottom: 1.6rem; }
.mode-card {
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.2rem;
    cursor: pointer;
    transition: all 0.15s;
    box-shadow: var(--shadow);
}
.mode-card:hover { border-color: var(--accent); box-shadow: var(--shadow-md); }
.mode-card.selected { border-color: var(--accent); background: var(--accent2); }
.mode-icon { font-size: 1.3rem; margin-bottom: 0.5rem; display: block; }
.mode-title { font-size: 0.88rem; font-weight: 600; color: var(--text); margin-bottom: 0.2rem; }
.mode-desc { font-size: 0.75rem; color: var(--muted); line-height: 1.5; }
.mode-apis {
    display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.6rem;
}
.api-tag {
    font-family: var(--mono); font-size: 0.58rem; font-weight: 500;
    padding: 0.15rem 0.5rem; border-radius: 4px;
    background: var(--surface2); color: var(--muted);
    border: 1px solid var(--border);
}
.api-tag.live { background: var(--green-bg); color: var(--green); border-color: #b2dfca; }

/* ── Input card ── */
.input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.3rem 1.4rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
.input-card-title {
    font-size: 0.78rem; font-weight: 600; color: var(--text);
    margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
}
.input-card-title span { color: var(--muted); font-weight: 400; font-size: 0.72rem; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: var(--bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 7px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.1) !important;
    background: white !important;
}
.stSelectbox div[data-baseweb="select"] {
    background: var(--bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 7px !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
}

/* ── Button ── */
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    transition: all 0.15s !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 2px 8px rgba(26,86,219,0.25) !important;
}
.stButton > button:hover {
    background: #1648c2 !important;
    box-shadow: 0 4px 12px rgba(26,86,219,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Expander ── */
.stExpander {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: var(--shadow) !important;
}
details summary { color: var(--muted) !important; font-size: 0.82rem !important; }

/* ── Divider ── */
.div { border: none; border-top: 1px solid var(--border); margin: 1.4rem 0; }

/* ── API response preview card ── */
.api-preview {
    background: #1a1714;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    font-family: var(--mono);
    font-size: 0.72rem;
    color: #a8c4a2;
    line-height: 1.7;
}
.api-preview-head {
    display: flex; align-items: center; gap: 0.6rem;
    margin-bottom: 0.7rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #2a2520;
}
.api-dot { width:8px; height:8px; border-radius:50%; }
.dot-r {background:#e06060;} .dot-y {background:#f0a500;} .dot-g {background:#7ec87e;}
.api-url { color: #6a8faf; font-size: 0.65rem; margin-left: 0.4rem; }
.api-key { color: #7ab3e0; }
.api-val { color: #a8c4a2; }
.api-num { color: #f0a500; }
.api-str { color: #e07070; }

/* ── Status bar ── */
.status-bar {
    display: flex; align-items: center; gap: 0.8rem;
    padding: 0.7rem 1.1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}
.s-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.s-run  { background: var(--amber); animation: blink 1.2s ease-in-out infinite; }
.s-done { background: var(--green); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.s-text { font-size: 0.82rem; color: var(--text); flex: 1; font-weight: 500; }
.s-meta { font-family: var(--mono); font-size: 0.65rem; color: var(--muted); }

/* ── Data cards (weather/crypto inline) ── */
.data-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.7rem; margin-bottom: 1rem; }
.data-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    box-shadow: var(--shadow);
}
.data-card-label { font-family: var(--mono); font-size: 0.58rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
.data-card-value { font-size: 1.2rem; font-weight: 700; color: var(--text); line-height: 1.1; }
.data-card-sub { font-size: 0.7rem; color: var(--muted); margin-top: 0.2rem; }
.data-card-up   { color: var(--green); }
.data-card-down { color: var(--red); }

/* ── Result panel ── */
.result-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}
.rp-head {
    display: flex; align-items: center; gap: 0.7rem; flex-wrap: wrap;
    padding: 0.85rem 1.2rem;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
}
.rp-badge {
    font-family: var(--mono); font-size: 0.6rem; font-weight: 600;
    padding: 0.2rem 0.6rem; border-radius: 5px;
    letter-spacing: 0.04em;
}
.b-blue   { background: var(--accent2); color: var(--accent); }
.b-green  { background: var(--green-bg); color: var(--green); }
.b-purple { background: var(--purple-bg); color: var(--purple); }
.b-amber  { background: var(--amber-bg); color: var(--amber); }
.rp-title { font-size: 0.78rem; font-weight: 500; color: var(--muted); }
.rp-body {
    padding: 1.2rem 1.3rem;
    font-family: var(--sans);
    font-size: 0.88rem;
    line-height: 1.85;
    color: var(--text);
    white-space: pre-wrap;
}

/* ── Stats row ── */
.stats-row { display:flex; flex-wrap:wrap; gap:0.5rem; margin: 0.8rem 0 1.2rem; }
.stat {
    font-family: var(--mono); font-size: 0.62rem; color: var(--muted);
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 5px; padding: 0.25rem 0.7rem;
    box-shadow: var(--shadow);
}
.stat b { color: var(--accent); }

/* ── Error ── */
.err-box {
    background: var(--red-bg); border: 1px solid #f5c6c3; border-left: 3px solid var(--red);
    border-radius: 8px; padding: 0.9rem 1.2rem;
    font-size: 0.82rem; color: #8b1c1c; line-height: 1.6;
}

/* ── Log ── */
.log-wrap {
    background: #1a1714; border-radius: 8px;
    overflow: hidden; margin-bottom: 1rem;
}
.log-head {
    display: flex; align-items: center; gap: 0.7rem;
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #2a2520;
}
.log-head-title { font-family: var(--mono); font-size: 0.6rem; color: #6a5f50; letter-spacing: 0.1em; text-transform: uppercase; }
.log-body { padding: 0.8rem 1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.log-line { display: flex; align-items: flex-start; gap: 0.7rem; font-family: var(--mono); font-size: 0.68rem; line-height: 1.5; }
.log-t { color: #4a4038; min-width: 48px; }
.log-tag { font-size: 0.56rem; font-weight: 700; padding: 0.1rem 0.4rem; border-radius: 3px; white-space: nowrap; margin-top: 0.15rem; }
.t-sys  { background:#2a2018; color:#8a7050; }
.t-agt  { background:#0e1e30; color:#6a9fd8; }
.t-api  { background:#0a1e0e; color:#6ac87e; }
.t-err  { background:#2a0e0e; color:#e07070; }
.log-msg { color: #c8b898; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="brand">
        <div class="brand-icon">◈</div>
        <div>
            <div class="brand-name">AgentForge</div>
            <div class="brand-tagline">live data intelligence · real api calls</div>
        </div>
    </div>
    <div class="topbar-right">
        <div class="live-pill"><div class="live-dot"></div>LIVE APIs</div>
        <div class="day-pill">DAY 5</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Mode selector ──────────────────────────────────────────────────────────────
st.markdown('<span class="sec-heading">Select Intelligence Mode</span>', unsafe_allow_html=True)

MODES = {
    "Weather Intelligence": {
        "icon": "⛅",
        "desc": "Real-time weather analysis for any city. Agent fetches live temperature, wind speed, humidity and generates a structured weather briefing.",
        "apis": ["Open-Meteo", "Geocoding API"],
    },
    "Crypto Market Intelligence": {
        "icon": "◈",
        "desc": "Live cryptocurrency price analysis. Agent fetches real market data and generates investment context, trend summary, and volatility assessment.",
        "apis": ["CoinGecko API", "Price Data"],
    },
    "Combined Market Brief": {
        "icon": "⬡",
        "desc": "Two specialized agents work together — one fetches weather data for a location, another fetches crypto prices — and a final agent synthesizes a unified market brief.",
        "apis": ["Open-Meteo", "CoinGecko API"],
    },
}

mode = st.radio("mode", list(MODES.keys()), label_visibility="collapsed", horizontal=True)
m = MODES[mode]

# Mode detail card
api_tags = "".join([f'<span class="api-tag live">{a}</span>' for a in m["apis"]])
st.markdown(f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;
padding:1rem 1.2rem;margin:0.6rem 0 1.4rem;box-shadow:var(--shadow);">
    <div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.4rem;">
        <span style="font-size:1.2rem;">{m["icon"]}</span>
        <span style="font-size:0.88rem;font-weight:600;color:var(--text);">{mode}</span>
    </div>
    <div style="font-size:0.78rem;color:var(--muted);line-height:1.6;margin-bottom:0.6rem;">{m["desc"]}</div>
    <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">{api_tags}</div>
</div>
""", unsafe_allow_html=True)

# ── Model selector ─────────────────────────────────────────────────────────────
MODELS = {
    "Gemini (Recommended)": {
        "gemini/gemini-2.5-flash": "Gemini 2.5 Flash  ✓ Free tier",
        "gemini/gemini-2.0-flash": "Gemini 2.0 Flash",
    },
    "Groq (Fallback)": {
        "groq/llama-3.3-70b-versatile": "LLaMA 3.3 70B",
        "groq/mixtral-8x7b-32768":      "Mixtral 8x7B",
    },
}

col_p, col_m = st.columns(2)
with col_p:
    st.markdown('<span class="sec-heading">Provider</span>', unsafe_allow_html=True)
    provider_choice = st.selectbox("prov", list(MODELS.keys()), label_visibility="collapsed")
with col_m:
    st.markdown('<span class="sec-heading">Model</span>', unsafe_allow_html=True)
    model_opts = MODELS[provider_choice]
    model_id = st.selectbox("mod", list(model_opts.keys()),
                             format_func=lambda x: model_opts[x], label_visibility="collapsed")

is_gemini = model_id.startswith("gemini/")

# ── Mode-specific inputs ────────────────────────────────────────────────────────
st.markdown('<div class="div"></div>', unsafe_allow_html=True)

city = "Dhaka"
coins = ["bitcoin", "ethereum", "solana"]

if mode == "Weather Intelligence":
    st.markdown('<span class="sec-heading">City</span>', unsafe_allow_html=True)
    city = st.text_input("city", value="Dhaka", placeholder="Enter any city name...",
                          label_visibility="collapsed")

elif mode == "Crypto Market Intelligence":
    st.markdown('<span class="sec-heading">Cryptocurrencies to Analyze</span>', unsafe_allow_html=True)
    coin_options = ["bitcoin", "ethereum", "solana", "cardano", "ripple", "dogecoin",
                    "polkadot", "chainlink", "avalanche-2", "matic-network"]
    coins = st.multiselect("coins", coin_options, default=["bitcoin", "ethereum", "solana"],
                            label_visibility="collapsed")
    if not coins:
        coins = ["bitcoin", "ethereum", "solana"]

elif mode == "Combined Market Brief":
    col_city, col_coins = st.columns(2)
    with col_city:
        st.markdown('<span class="sec-heading">City</span>', unsafe_allow_html=True)
        city = st.text_input("city2", value="Dhaka", placeholder="City name...", label_visibility="collapsed")
    with col_coins:
        st.markdown('<span class="sec-heading">Crypto Assets</span>', unsafe_allow_html=True)
        coin_options = ["bitcoin", "ethereum", "solana", "cardano", "ripple", "dogecoin"]
        coins = st.multiselect("coins2", coin_options, default=["bitcoin", "ethereum"],
                                label_visibility="collapsed")
        if not coins:
            coins = ["bitcoin", "ethereum"]

with st.expander("⚙  Advanced Settings"):
    analysis_depth = st.select_slider("Analysis Depth", ["Brief", "Standard", "Detailed"], value="Standard")
    include_recommendation = st.checkbox("Include actionable recommendations", value=True)
    audience = st.selectbox("Target Audience",
        ["General", "Investor", "Business Analyst", "Travel Planner"], index=1)

st.markdown('<div class="div"></div>', unsafe_allow_html=True)
run_btn = st.button("◈  FETCH LIVE DATA & RUN AGENTS")


# ── Execution ──────────────────────────────────────────────────────────────────
if run_btn:
    try:
        from crewai import Agent, Task, Crew, LLM
        from crewai.tools import BaseTool
        from typing import ClassVar, List
    except ImportError as e:
        st.markdown(f'<div class="err-box">Import error: {e}<br>Make sure crewai is in requirements.txt</div>', unsafe_allow_html=True)
        st.stop()

    api_key = os.environ.get("GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY", "")
    if not api_key:
        st.markdown(f'<div class="err-box">⚠ {"GEMINI_API_KEY" if is_gemini else "GROQ_API_KEY"} not found in Streamlit Secrets.</div>', unsafe_allow_html=True)
        st.stop()

    if is_gemini:
        os.environ["GEMINI_API_KEY"] = api_key

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
            <div class="log-head">{' '.join(['<div style="width:8px;height:8px;border-radius:50%;background:' + c + '"></div>' for c in ['#e06060','#f0a500','#7ec87e']])}
            <span class="log-head-title">API + Agent Execution Log</span></div>
            <div class="log-body">{rows}</div>
        </div>""", unsafe_allow_html=True)

    log = []
    provider_label = "gemini" if is_gemini else "groq"
    log.append((ts(), "SYS", "t-sys", f"Mode: {mode} · Provider: {provider_label} · {model_id.split('/')[1]}"))
    render_log(log)

    # ── Define Tools ───────────────────────────────────────────────────────────

    class WeatherTool(BaseTool):
        name: str = "Weather Data Tool"
        description: str = (
            "Fetches real-time weather data for any city using the Open-Meteo API (no API key required). "
            "Returns current temperature in Celsius, wind speed in km/h, humidity percentage, "
            "and weather condition code. Always use this tool when weather data is needed. "
            "Input should be the city name as a string."
        )
        def _run(self, city: str) -> str:
            try:
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city.strip()}&count=1"
                geo = requests.get(geo_url, timeout=8).json()
                if "results" not in geo or not geo["results"]:
                    return f"City '{city}' not found. Please try a different city name."
                r = geo["results"][0]
                lat, lon = r["latitude"], r["longitude"]
                country = r.get("country", "Unknown")
                w_url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,"
                    f"apparent_temperature,weather_code,precipitation"
                    f"&wind_speed_unit=kmh&timezone=auto"
                )
                w = requests.get(w_url, timeout=8).json()
                c = w.get("current", {})
                wmo_codes = {
                    0:"Clear sky", 1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
                    45:"Fog", 48:"Icy fog", 51:"Light drizzle", 53:"Moderate drizzle",
                    61:"Slight rain", 63:"Moderate rain", 65:"Heavy rain",
                    71:"Slight snow", 73:"Moderate snow", 75:"Heavy snow",
                    80:"Slight showers", 81:"Moderate showers", 82:"Violent showers",
                    95:"Thunderstorm", 96:"Thunderstorm with hail",
                }
                condition = wmo_codes.get(c.get("weather_code", 0), "Unknown")
                return (
                    f"City: {city.title()}, {country} | "
                    f"Temperature: {c.get('temperature_2m','N/A')}°C | "
                    f"Feels Like: {c.get('apparent_temperature','N/A')}°C | "
                    f"Humidity: {c.get('relative_humidity_2m','N/A')}% | "
                    f"Wind Speed: {c.get('wind_speed_10m','N/A')} km/h | "
                    f"Condition: {condition} | "
                    f"Precipitation: {c.get('precipitation','N/A')}mm"
                )
            except requests.exceptions.Timeout:
                return "Weather API timeout. Please try again."
            except Exception as ex:
                return f"Weather API error: {str(ex)}"

    class CryptoPriceTool(BaseTool):
        name: str = "Crypto Price Tool"
        description: str = (
            "Fetches real-time cryptocurrency prices, market cap, 24h price change percentage, "
            "and trading volume from the CoinGecko public API (no API key required). "
            "Use this tool when cryptocurrency market data is needed. "
            "Input should be comma-separated coin IDs (e.g. 'bitcoin,ethereum,solana')."
        )
        def _run(self, coin_ids: str) -> str:
            try:
                ids = coin_ids.strip().replace(" ", "").lower()
                url = (
                    f"https://api.coingecko.com/api/v3/simple/price?"
                    f"ids={ids}&vs_currencies=usd"
                    f"&include_market_cap=true&include_24hr_change=true&include_24hr_vol=true"
                )
                data = requests.get(url, timeout=10).json()
                if not data:
                    return f"No price data returned for: {coin_ids}"
                results = []
                for coin_id, vals in data.items():
                    price     = vals.get("usd", "N/A")
                    change_24 = round(vals.get("usd_24h_change", 0), 2)
                    mcap      = vals.get("usd_market_cap", 0)
                    vol       = vals.get("usd_24h_vol", 0)
                    direction = "▲" if change_24 >= 0 else "▼"
                    results.append(
                        f"{coin_id.upper()}: ${price:,.2f} | "
                        f"24h: {direction}{abs(change_24)}% | "
                        f"Market Cap: ${mcap/1e9:.1f}B | "
                        f"Volume: ${vol/1e6:.1f}M"
                    )
                return "\n".join(results)
            except requests.exceptions.Timeout:
                return "CoinGecko API timeout. Please try again in a moment."
            except Exception as ex:
                return f"Crypto API error: {str(ex)}"

    # ── Live API preview (before agents run) ──────────────────────────────────
    live_data_display = {}

    if mode in ["Weather Intelligence", "Combined Market Brief"]:
        log.append((ts(), "API", "t-api", f"Calling Open-Meteo Geocoding API → city: {city}"))
        render_log(log)
        try:
            geo = requests.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={city.strip()}&count=1",
                timeout=6).json()
            if "results" in geo and geo["results"]:
                r = geo["results"][0]
                lat, lon = r["latitude"], r["longitude"]
                w = requests.get(
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                    f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,"
                    f"apparent_temperature,weather_code&timezone=auto",
                    timeout=6).json()
                c = w.get("current", {})
                live_data_display["weather"] = {
                    "temp": c.get("temperature_2m", "N/A"),
                    "feels": c.get("apparent_temperature", "N/A"),
                    "humidity": c.get("relative_humidity_2m", "N/A"),
                    "wind": c.get("wind_speed_10m", "N/A"),
                    "city": city.title(),
                    "country": r.get("country", ""),
                }
                log.append((ts(), "API", "t-api", f"Open-Meteo responded ✓ — {city.title()}: {c.get('temperature_2m')}°C, Wind: {c.get('wind_speed_10m')} km/h"))
                render_log(log)
        except Exception as ex:
            log.append((ts(), "ERR", "t-err", f"Weather API error: {str(ex)[:60]}"))
            render_log(log)

    if mode in ["Crypto Market Intelligence", "Combined Market Brief"]:
        coin_str = ",".join(coins)
        log.append((ts(), "API", "t-api", f"Calling CoinGecko API → {coin_str}"))
        render_log(log)
        try:
            data = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={coin_str}"
                f"&vs_currencies=usd&include_24hr_change=true&include_market_cap=true",
                timeout=8).json()
            live_data_display["crypto"] = data
            coin_summary = " | ".join([
                f"{k.upper()}: ${v.get('usd',0):,.0f}" for k, v in data.items()
            ])
            log.append((ts(), "API", "t-api", f"CoinGecko responded ✓ — {coin_summary}"))
            render_log(log)
        except Exception as ex:
            log.append((ts(), "ERR", "t-err", f"Crypto API error: {str(ex)[:60]}"))
            render_log(log)

    # ── Show live data cards ────────────────────────────────────────────────────
    if "weather" in live_data_display:
        wd = live_data_display["weather"]
        st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <span class="sec-heading">Live Weather Data — {wd['city']}, {wd['country']}</span>
        </div>
        <div class="data-cards">
            <div class="data-card">
                <div class="data-card-label">Temperature</div>
                <div class="data-card-value">{wd['temp']}°C</div>
                <div class="data-card-sub">Feels like {wd['feels']}°C</div>
            </div>
            <div class="data-card">
                <div class="data-card-label">Humidity</div>
                <div class="data-card-value">{wd['humidity']}%</div>
                <div class="data-card-sub">Relative humidity</div>
            </div>
            <div class="data-card">
                <div class="data-card-label">Wind Speed</div>
                <div class="data-card-value">{wd['wind']}</div>
                <div class="data-card-sub">km/h</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if "crypto" in live_data_display:
        crypto_data = live_data_display["crypto"]
        st.markdown('<span class="sec-heading">Live Crypto Prices</span>', unsafe_allow_html=True)
        cols_data = st.columns(min(len(crypto_data), 4))
        for i, (coin, vals) in enumerate(list(crypto_data.items())[:4]):
            price  = vals.get("usd", 0)
            change = round(vals.get("usd_24h_change", 0), 2)
            cls    = "data-card-up" if change >= 0 else "data-card-down"
            arrow  = "▲" if change >= 0 else "▼"
            with cols_data[i % len(cols_data)]:
                st.markdown(f"""
                <div class="data-card">
                    <div class="data-card-label">{coin.upper()}</div>
                    <div class="data-card-value">${price:,.2f}</div>
                    <div class="data-card-sub {cls}">{arrow} {abs(change)}% 24h</div>
                </div>""", unsafe_allow_html=True)

    # ── Build and run crew ─────────────────────────────────────────────────────
    log.append((ts(), "AGT", "t-agt", "Building agents with live API tools…"))
    render_log(log)

    status_ph.markdown("""
    <div class="status-bar">
        <div class="s-dot s-run"></div>
        <span class="s-text">Agents running — calling live APIs and analyzing data…</span>
    </div>""", unsafe_allow_html=True)

    depth_map = {"Brief": "2–3 sentences per section", "Standard": "1–2 paragraphs per section", "Detailed": "comprehensive deep-dive per section"}
    depth_instruction = depth_map.get(analysis_depth, "1–2 paragraphs per section")
    rec_instruction = "Include specific actionable recommendations." if include_recommendation else "Analysis only, no recommendations."
    audience_instruction = f"Target audience: {audience}. Adjust tone and depth accordingly."

    try:
        llm = LLM(model=model_id, api_key=api_key, temperature=0.7)
        coin_str = ",".join(coins)

        if mode == "Weather Intelligence":
            weather_tool = WeatherTool()
            agent = Agent(
                role="Weather Intelligence Analyst",
                goal=f"Use the Weather Data Tool to fetch real-time weather for {city} and produce a structured weather briefing.",
                backstory=f"You are a data-driven meteorological analyst. You always call the Weather Data Tool before writing any analysis. {audience_instruction}",
                tools=[weather_tool], llm=llm, verbose=False,
            )
            task = Task(
                description=f"Fetch current weather for {city} using the Weather Data Tool. {rec_instruction} Depth: {depth_instruction}",
                expected_output=f"Weather Intelligence Report for {city} with: Current Conditions, Comfort Index, Wind & Humidity Analysis, and Outlook. {rec_instruction}",
                agent=agent,
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)

        elif mode == "Crypto Market Intelligence":
            crypto_tool = CryptoPriceTool()
            agent = Agent(
                role="Crypto Market Intelligence Analyst",
                goal=f"Use the Crypto Price Tool to fetch live prices for {coin_str} and generate a market intelligence report.",
                backstory=f"You are a quantitative crypto analyst. You always call the Crypto Price Tool first. {audience_instruction}",
                tools=[crypto_tool], llm=llm, verbose=False,
            )
            task = Task(
                description=f"Fetch live crypto data for {coin_str} using the Crypto Price Tool. Analyze price levels, 24h movements, and market context. {rec_instruction} Depth: {depth_instruction}",
                expected_output=f"Crypto Market Report covering: Price Summary, 24h Movement Analysis, Market Sentiment, and Outlook. {rec_instruction}",
                agent=agent,
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)

        else:  # Combined
            weather_tool = WeatherTool()
            crypto_tool  = CryptoPriceTool()

            weather_agent = Agent(
                role="Weather Data Specialist",
                goal=f"Fetch and analyze real-time weather data for {city}.",
                backstory=f"Expert meteorological data analyst. Always uses Weather Data Tool. {audience_instruction}",
                tools=[weather_tool], llm=llm, verbose=False,
            )
            crypto_agent = Agent(
                role="Crypto Market Specialist",
                goal=f"Fetch and analyze live prices for {coin_str}.",
                backstory=f"Quantitative crypto analyst. Always uses Crypto Price Tool. {audience_instruction}",
                tools=[crypto_tool], llm=llm, verbose=False,
            )
            weather_task = Task(
                description=f"Fetch weather for {city}. Depth: {depth_instruction}",
                expected_output=f"Weather briefing for {city}: conditions, comfort, outlook.",
                agent=weather_agent,
            )
            crypto_task = Task(
                description=f"Fetch prices for {coin_str}. {rec_instruction} Depth: {depth_instruction}",
                expected_output=f"Crypto market brief: prices, 24h movement, sentiment. {rec_instruction}",
                agent=crypto_agent,
                context=[weather_task],
            )
            crew = Crew(
                agents=[weather_agent, crypto_agent],
                tasks=[weather_task, crypto_task],
                verbose=False,
            )

        result = crew.kickoff()
        elapsed = round(time.time() - t0, 1)

        # Extract outputs
        out1, out2 = "", ""
        try:
            if mode == "Combined Market Brief":
                out1 = str(weather_task.output.raw) if weather_task.output else ""
                out2 = str(crypto_task.output.raw)  if crypto_task.output  else ""
            else:
                out1 = str(task.output.raw) if task.output else str(result)
        except Exception:
            out1 = str(result)

        log.append((ts(), "API", "t-api", "All API calls completed ✓"))
        log.append((ts(), "AGT", "t-agt", f"Agent analysis complete in {elapsed}s"))
        render_log(log)

        status_ph.markdown(f"""
        <div class="status-bar">
            <div class="s-dot s-done"></div>
            <span class="s-text">Analysis complete — live data fetched and processed</span>
            <span class="s-meta">{elapsed}s</span>
        </div>""", unsafe_allow_html=True)

        agent_count = 2 if mode == "Combined Market Brief" else 1
        api_list = "Open-Meteo + CoinGecko" if mode == "Combined Market Brief" else ("Open-Meteo" if "Weather" in mode else "CoinGecko")
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat">mode <b>{mode}</b></div>
            <div class="stat">agents <b>{agent_count}</b></div>
            <div class="stat">live apis <b>{api_list}</b></div>
            <div class="stat">elapsed <b>{elapsed}s</b></div>
            <div class="stat">model <b>{model_id.split('/')[1]}</b></div>
            <div class="stat">depth <b>{analysis_depth}</b></div>
        </div>""", unsafe_allow_html=True)

        if mode == "Combined Market Brief":
            if out1:
                st.markdown(f"""
                <div class="result-panel">
                    <div class="rp-head">
                        <span class="rp-badge b-blue">Weather Specialist</span>
                        <span class="rp-badge b-green">Open-Meteo API ✓</span>
                        <span class="rp-title">{city.title()} Weather Intelligence</span>
                    </div>
                    <div class="rp-body">{out1}</div>
                </div>""", unsafe_allow_html=True)
            if out2:
                st.markdown(f"""
                <div class="result-panel">
                    <div class="rp-head">
                        <span class="rp-badge b-purple">Crypto Specialist</span>
                        <span class="rp-badge b-green">CoinGecko API ✓</span>
                        <span class="rp-title">Crypto Market Intelligence</span>
                    </div>
                    <div class="rp-body">{out2}</div>
                </div>""", unsafe_allow_html=True)
        else:
            badge_color = "b-blue" if "Weather" in mode else "b-purple"
            api_badge = "Open-Meteo API ✓" if "Weather" in mode else "CoinGecko API ✓"
            st.markdown(f"""
            <div class="result-panel">
                <div class="rp-head">
                    <span class="rp-badge {badge_color}">Intelligence Analyst</span>
                    <span class="rp-badge b-green">{api_badge}</span>
                    <span class="rp-badge b-amber">{analysis_depth} · {audience}</span>
                    <span class="rp-title">Live Data Analysis</span>
                </div>
                <div class="rp-body">{out1}</div>
            </div>""", unsafe_allow_html=True)

    except Exception as e:
        err_str = str(e)
        log.append((ts(), "ERR", "t-err", "Execution failed"))
        render_log(log)
        status_ph.empty()

        if "resource_exhausted" in err_str.lower() or "quota" in err_str.lower() or "429" in err_str:
            st.markdown('<div class="err-box"><b>Quota Exhausted (429)</b><br><br>Switch to Gemini 2.5 Flash or wait 60 seconds and retry. Gemini 2.0 Flash has limited free-tier quota.</div>', unsafe_allow_html=True)
        elif "rate_limit" in err_str.lower():
            st.markdown('<div class="err-box"><b>Rate limit hit.</b> Wait 30–60 seconds and retry.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="err-box"><b>Error:</b> {err_str}</div>', unsafe_allow_html=True)
