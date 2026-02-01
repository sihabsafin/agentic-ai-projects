import streamlit as st
import os
import time
import json
from datetime import datetime, timedelta
import pytz

# ── LangChain imports (UPDATED - fixed import paths) ──
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# ── local imports ──
from firebase_config import (
    sign_up, sign_in, get_db, get_user_data,
    track_message, track_document_upload,
    track_response_time, track_rating,
    get_all_users, get_usage_logs,
    get_performance_logs, get_ratings,
    check_message_limit, check_document_limit,
    create_checkout_session, upgrade_to_premium,
    verify_stripe_session,
    FREE_PLAN_LIMITS, PREMIUM_PLAN_LIMITS,
)

# ─────────────────────────────────────────────
# Page Config & Global CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Apex AI – RAG Chatbot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ═══════════════════════════════════════════════════════════
   🎨 GRADIENT GLASSMORPHISM DESIGN - Premium & Modern
   ═══════════════════════════════════════════════════════════ */

/* ── 1. GLOBAL FOUNDATION ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
    background-attachment: fixed;
}

/* ── 2. GLASSMORPHIC CARDS ── */
.glass-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2);
}

/* ── 3. METRIC CARDS - Glassmorphic ── */
.metric-card {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 18px;
    padding: 24px 20px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.metric-card:hover {
    transform: translateY(-4px) scale(1.02);
    border-color: rgba(139, 92, 246, 0.4);
    box-shadow: 0 16px 48px rgba(99, 102, 241, 0.25);
}

.metric-card.user { border-color: rgba(99, 102, 241, 0.3); }
.metric-card.usage { border-color: rgba(34, 211, 238, 0.3); }
.metric-card.rev { border-color: rgba(52, 211, 153, 0.3); }
.metric-card.perf { border-color: rgba(251, 146, 60, 0.3); }

.metric-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #94a3b8;
    margin-bottom: 8px;
    font-weight: 600;
}

.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f1f5f9 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}

.metric-card .change {
    font-size: 0.75rem;
    margin-top: 8px;
    color: #64748b;
}

.metric-card .change .up { color: #34d399; }
.metric-card .change .down { color: #f87171; }

/* ── 4. CHAT INTERFACE - Premium Mobile-First ── */
.chat-container {
    max-height: 60vh;
    overflow-y: auto;
    padding: 20px;
    scroll-behavior: smooth;
}

/* Custom Scrollbar */
.chat-container::-webkit-scrollbar {
    width: 6px;
}

.chat-container::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.3);
    border-radius: 10px;
}

.chat-container::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
}

/* Chat Messages */
.chat-msg {
    margin-bottom: 16px;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.chat-msg.user { text-align: right; }

.chat-msg .bubble {
    display: inline-block;
    max-width: 85%;
    padding: 14px 18px;
    border-radius: 20px;
    font-size: 0.95rem;
    line-height: 1.6;
    word-wrap: break-word;
    position: relative;
}

/* User Bubble - Gradient Glass */
.chat-msg.user .bubble {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #ffffff;
    border-bottom-right-radius: 6px;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
}

/* Bot Bubble - Frosted Glass */
.chat-msg.bot .bubble {
    background: rgba(30, 41, 59, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #e2e8f0;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-bottom-left-radius: 6px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* ── 5. AUTH FORMS - Glassmorphic ── */
.auth-container {
    max-width: 480px;
    margin: 60px auto;
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 24px;
    padding: 48px 40px;
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.5);
    animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.auth-header {
    text-align: center;
    margin-bottom: 36px;
}

.auth-header h1 {
    background: linear-gradient(135deg, #f1f5f9 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.2rem;
    margin: 0 0 12px 0;
    font-weight: 700;
}

.auth-header .subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
}

/* Auth Tabs */
.auth-tabs {
    display: flex;
    gap: 12px;
    margin-bottom: 32px;
}

.auth-tab {
    flex: 1;
    padding: 14px;
    text-align: center;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 12px;
    color: #94a3b8;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.auth-tab:hover {
    background: rgba(99, 102, 241, 0.1);
    border-color: rgba(99, 102, 241, 0.4);
}

.auth-tab.active {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border-color: transparent;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
}

/* ── 6. BADGES & CTAs ── */
.premium-badge {
    display: inline-block;
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: #0f172a;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.limit-warning {
    background: rgba(251, 191, 36, 0.15);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(251, 191, 36, 0.4);
    border-radius: 12px;
    padding: 16px;
    color: #fbbf24;
    margin: 16px 0;
}

.upgrade-cta {
    background: linear-gradient(135deg, #34d399, #10b981);
    color: white;
    padding: 18px 28px;
    border-radius: 14px;
    text-align: center;
    margin: 24px 0;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
}

.upgrade-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(16, 185, 129, 0.4);
}

/* ── 7. SIDEBAR NAVIGATION ── */
.sidebar-nav a {
    display: block;
    padding: 12px 18px;
    color: #cbd5e1;
    text-decoration: none;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 500;
    transition: all 0.3s ease;
    margin-bottom: 6px;
    backdrop-filter: blur(8px);
}

.sidebar-nav a:hover {
    background: rgba(99, 102, 241, 0.2);
    color: #c7d2fe;
    transform: translateX(4px);
}

.sidebar-nav a.active {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.3));
    border-left: 3px solid #6366f1;
    color: #c7d2fe;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
}

/* ── 8. TABLES ── */
.dash-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    color: #cbd5e1;
}

.dash-table th {
    text-align: left;
    padding: 12px 14px;
    background: rgba(30, 41, 59, 0.6);
    color: #94a3b8;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 1px solid rgba(99, 102, 241, 0.2);
}

.dash-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(51, 65, 85, 0.3);
}

.dash-table tr:hover td {
    background: rgba(99, 102, 241, 0.08);
}

/* ── 9. SECTION TITLES ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    background: linear-gradient(135deg, #94a3b8 0%, #c7d2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 32px 0 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(99, 102, 241, 0.3);
}

/* ── 10. STREAMLIT WIDGET OVERRIDES ── */
.stTextInput input, .stTextArea textarea {
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    color: #f1f5f9 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(139, 92, 246, 0.6) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

.stButton button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(99, 102, 241, 0.4) !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(12px);
    border: 2px dashed rgba(99, 102, 241, 0.4);
    border-radius: 16px;
    padding: 24px;
}

/* ── 11. MOBILE RESPONSIVE (Mobile-First) ── */
@media (max-width: 768px) {
    .auth-container {
        margin: 20px;
        padding: 32px 24px;
    }
    
    .metric-card {
        padding: 18px 16px;
    }
    
    .metric-card .value {
        font-size: 1.6rem;
    }
    
    .chat-msg .bubble {
        max-width: 90%;
        font-size: 0.9rem;
        padding: 12px 16px;
    }
    
    .chat-container {
        max-height: 50vh;
        padding: 12px;
    }
}

/* ── 12. RATING STARS ── */
.star {
    cursor: pointer;
    font-size: 1.8rem;
    color: rgba(51, 65, 85, 0.5);
    transition: all 0.2s ease;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.star:hover, .star.active {
    color: #fbbf24;
    transform: scale(1.2);
    filter: drop-shadow(0 4px 8px rgba(251, 191, 36, 0.5));
}

/* ── 13. LOADING ANIMATIONS ── */
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.loading {
    background: linear-gradient(90deg, rgba(30, 41, 59, 0.6) 0%, rgba(99, 102, 241, 0.3) 50%, rgba(30, 41, 59, 0.6) 100%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}

/* ── 14. ACCESSIBILITY ── */
:focus-visible {
    outline: 2px solid #8b5cf6;
    outline-offset: 2px;
}

/* ── 15. SMOOTH TRANSITIONS ── */
* {
    transition: background-color 0.3s ease, border-color 0.3s ease;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LangChain Setup (UNCHANGED - existing AI logic)
# ─────────────────────────────────────────────
def setup_langchain():
    """Configure LangSmith tracing if API keys are available."""
    langsmith_api_key = os.environ.get("LANGSMITH_API_KEY") or st.secrets.get("LANGSMITH_API_KEY", "")
    
    if langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = st.secrets.get("LANGCHAIN_PROJECT", "apex-ai-rag")
        st.sidebar.caption("🔍 LangSmith tracing: **enabled**")
    else:
        st.sidebar.caption("🔍 LangSmith tracing: **disabled** (no API key)")

setup_langchain()


@st.cache_resource
def load_embeddings():
    """Load HuggingFace embeddings model (cached)."""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )


@st.cache_resource
def build_vector_store():
    """Build FAISS vector store from knowledge.txt (cached)."""
    kb_path = os.path.join(os.path.dirname(__file__), "knowledge.txt")
    
    if not os.path.exists(kb_path):
        st.warning("⚠️ knowledge.txt not found. Using empty knowledge base.")
        return None
    
    with open(kb_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Split into chunks - UPGRADED for better context
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # 3x larger chunks for more context
        chunk_overlap=200,  # 4x more overlap to preserve relationships
        separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]
    )
    chunks = splitter.split_text(text)
    
    if not chunks:
        return None
    
    # Create FAISS vector store
    embeddings = load_embeddings()
    vectorstore = FAISS.from_texts(chunks, embeddings)
    
    return vectorstore


def get_rag_chain():
    """Create Groq-powered RAG chain (Modern LangChain Compatible)."""

    groq_api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not groq_api_key:
        st.error("❌ GROQ_API_KEY not found in secrets!")
        return None

    # ✅ Groq LLM - UPGRADED for maximum intelligence
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",  # Most powerful Groq model
        temperature=0.3,  # Lower temp for more focused, accurate responses
        max_tokens=4096,  # 4x more tokens for detailed answers
    )

    # ✅ Vector Store
    vectorstore = build_vector_store()
    if not vectorstore:
        st.warning("⚠️ No knowledge base loaded.")
        return None

    # ✅ UPGRADED Retriever - fetch more relevant context
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance for diverse results
        search_kwargs={
            "k": 6,  # 2x more chunks for comprehensive context
            "fetch_k": 12,  # Fetch more candidates before filtering
            "lambda_mult": 0.7  # Balance between relevance and diversity
        }
    )

    # ✅ UPGRADED Prompt - Advanced reasoning and comprehensive analysis
    prompt = ChatPromptTemplate.from_template(
        """You are Apex AI, an advanced AI assistant with deep analytical capabilities.

Your goal is to provide intelligent, comprehensive, and accurate answers by:
1. Carefully analyzing all provided context
2. Synthesizing information from multiple sources
3. Providing detailed explanations with reasoning
4. Being specific and precise in your responses
5. Citing relevant information when available

**Context from Knowledge Base:**
{context}

**User Question:**
{question}

**Instructions:**
- If the context contains relevant information, use it to provide a detailed, well-reasoned answer
- Explain the reasoning behind your answer
- If you find multiple relevant pieces of information, synthesize them coherently
- If the context doesn't fully answer the question, say so clearly and provide what you can
- Be specific with examples, numbers, or details from the context when available
- Structure complex answers with clear points

**Your Response:**"""
    )

    # ✅ Modern RAG Chain (LCEL)
    from operator import itemgetter
    
    rag_chain = (
        {
            "context": itemgetter("question") | retriever,
            "question": itemgetter("question")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain



# ─────────────────────────────────────────────
# Session State Helpers
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "authenticated": False,
        "uid": None,
        "email": None,
        "role": "user",  # NEW: track user role
        "full_name": "",  # NEW: track user's full name
        "page": "chat",
        "chat_history": [],
        "rag_chain": None,
        "auth_mode": "signin",  # NEW: track signin/signup mode
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# Handle Stripe redirect (check for upgrade success)
query_params = st.query_params
if "upgrade" in query_params and query_params["upgrade"] == "success":
    if "session_id" in query_params:
        session_id = query_params["session_id"]
        session_data = verify_stripe_session(session_id)
        
        if session_data and st.session_state.uid:
            upgrade_to_premium(st.session_state.uid, session_id)
            st.success("🎉 Successfully upgraded to Premium!")
            st.balloons()


# ─────────────────────────────────────────────
# Sidebar (UPDATED with role-based navigation)
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚡ Apex AI", unsafe_allow_html=False)
        st.caption("Powered by **Groq** + **Llama 3.3 70B**")
        st.divider()

        if st.session_state.authenticated:
            # Show user info with plan badge
            user_data = get_user_data(st.session_state.uid)
            plan = user_data.get("plan", "free") if user_data else "free"
            
            if plan == "premium":
                st.markdown(
                    '<div style="text-align: center;"><span class="premium-badge">⭐ Premium</span></div>',
                    unsafe_allow_html=True
                )
            
            st.caption(f"👤 **{st.session_state.full_name}**")
            st.caption(f"📧 {st.session_state.email}")
            
            st.divider()
            
            # Navigation based on role
            if st.session_state.role == "admin":
                # Admin navigation
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💬 Chat", use_container_width=True):
                        st.session_state.page = "chat"
                        st.rerun()
                with col2:
                    if st.button("📊 My Stats", use_container_width=True):
                        st.session_state.page = "user_dashboard"
                        st.rerun()
                with col3:
                    if st.button("🎛️ Admin", use_container_width=True):
                        st.session_state.page = "admin_dashboard"
                        st.rerun()
            else:
                # Regular user navigation
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💬 Chat", use_container_width=True):
                        st.session_state.page = "chat"
                        st.rerun()
                with col2:
                    if st.button("📊 Dashboard", use_container_width=True):
                        st.session_state.page = "user_dashboard"
                        st.rerun()

            st.divider()
            if st.button("Logout", use_container_width=True):
                st.session_state.clear()
                init_session()
                st.rerun()
        else:
            st.info("Sign in to get started.")

render_sidebar()


# ─────────────────────────────────────────────
# Auth Page (FIXED - no auto-refresh)
# ─────────────────────────────────────────────
def render_auth():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="auth-header">
        <h1>⚡ Apex AI</h1>
        <div class="subtitle">Enterprise-grade RAG chatbot powered by Llama 3.3 70B</div>
    </div>
    """, unsafe_allow_html=True)

    # Tab selection with session state to maintain form data
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", use_container_width=True, key="signin_tab", 
                    type="primary" if st.session_state.auth_mode == "signin" else "secondary"):
            st.session_state.auth_mode = "signin"
            st.rerun()
    with col2:
        if st.button("Create Account", use_container_width=True, key="signup_tab",
                    type="primary" if st.session_state.auth_mode == "signup" else "secondary"):
            st.session_state.auth_mode = "signup"
            st.rerun()
    
    st.divider()

    # Sign In Form
    if st.session_state.auth_mode == "signin":
        st.markdown("### Sign In to Your Account")
        
        with st.form("signin_form", clear_on_submit=False):
            email = st.text_input("Email Address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    st.error("❌ Please fill in both fields.")
                else:
                    try:
                        with st.spinner("Signing in..."):
                            result = sign_in(email, password)
                            st.session_state.authenticated = True
                            st.session_state.uid = result["localId"]
                            st.session_state.email = result["email"]
                            st.session_state.role = result.get("role", "user")
                            st.session_state.full_name = result.get("full_name", "")
                            st.session_state.page = "chat"
                            st.success("✅ Welcome back!")
                            time.sleep(0.5)
                            st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "INVALID_LOGIN_CREDENTIALS" in error_msg or "INVALID_PASSWORD" in error_msg:
                            st.error("❌ Invalid email or password. Please try again.")
                        else:
                            st.error(f"❌ Sign-in failed: {error_msg}")
        
        st.caption("Don't have an account? Click 'Create Account' above.")
    
    # Sign Up Form
    else:
        st.markdown("### Create Your Account")
        
        with st.form("signup_form", clear_on_submit=False):
            full_name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email Address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            st.caption("🔒 Password must be at least 6 characters")
            
            submitted = st.form_submit_button("Create Account →", use_container_width=True)
            
            if submitted:
                if not full_name or not email or not password:
                    st.error("❌ Please fill in all fields.")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                else:
                    try:
                        with st.spinner("Creating your account..."):
                            sign_up(email, password, full_name)
                            st.success("✅ Account created successfully! Please sign in.")
                            st.session_state.auth_mode = "signin"  # Switch to sign in
                            time.sleep(1.5)
                            st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "EMAIL_EXISTS" in error_msg or "EMAIL_ALREADY_EXISTS" in error_msg:
                            st.error("❌ This email is already registered. Please sign in.")
                        elif "WEAK_PASSWORD" in error_msg:
                            st.error("❌ Password is too weak. Use at least 6 characters.")
                        else:
                            st.error(f"❌ Sign-up failed: {error_msg}")
        
        st.caption("Already have an account? Click 'Sign In' above.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RAG Chatbot Page (UPDATED with usage limits)
# ─────────────────────────────────────────────
def render_chat():
    # Get user data for limit checking
    user_data = get_user_data(st.session_state.uid)
    plan = user_data.get("plan", "free") if user_data else "free"
    
    # Check message limit
    can_send, msgs_remaining, msgs_limit = check_message_limit(st.session_state.uid)
    
    # Show limit warning if approaching limit
    if plan == "free" and msgs_remaining <= 10 and msgs_remaining > 0:
        st.markdown(f"""
        <div class="limit-warning">
            ⚠️ <strong>Warning:</strong> You have only {msgs_remaining} messages remaining on your Free plan.
            <a href="#upgrade" style="color: #fbbf24; text-decoration: underline;">Upgrade to Premium</a> for unlimited messages!
        </div>
        """, unsafe_allow_html=True)
    
    # Show upgrade required if limit reached
    if not can_send:
        st.markdown("""
        <div class="upgrade-cta">
            <h3 style="margin: 0 0 12px 0;">🚀 Upgrade to Premium</h3>
            <p style="margin: 0 0 16px 0;">You've reached your Free plan limit of 100 messages.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⭐ Upgrade to Premium - $9.99/month", use_container_width=True):
            checkout_url = create_checkout_session(st.session_state.uid, st.session_state.email)
            if checkout_url:
                st.markdown(f'<meta http-equiv="refresh" content="0; url={checkout_url}">', unsafe_allow_html=True)
        
        return  # Don't render chat interface
    
    # Initialize RAG chain (only once per session)
    if st.session_state.rag_chain is None:
        with st.spinner("🔄 Loading RAG system..."):
            st.session_state.rag_chain = get_rag_chain()
    
    # Chat history display
    st.markdown('<div style="height:420px; overflow-y:auto; padding:10px 0;" id="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        role_cls = "user" if msg["role"] == "user" else "bot"
        content = msg["content"]
        
        # Show sources if available
        if msg["role"] == "assistant" and "sources" in msg:
            sources = msg["sources"]
            if sources:
                content += f"\n\n<small style='color:#64748b;'>📚 Sources: {len(sources)} chunks retrieved</small>"
        
        st.markdown(
            f'<div class="chat-msg {role_cls}"><div class="bubble">{content}</div></div>',
            unsafe_allow_html=True,
        )
    
    if not st.session_state.chat_history:
        welcome_msg = f"👋 Hi <strong>{st.session_state.full_name or 'there'}</strong>! I'm <strong>Apex AI</strong> powered by <strong>Llama 3.3 70B</strong> via Groq."
        if plan == "free":
            welcome_msg += f" You have <strong>{msgs_remaining} messages</strong> remaining on your Free plan."
        st.markdown(
            f'<div class="chat-msg bot"><div class="bubble">{welcome_msg}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Input row
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "", placeholder="Type your message…",
            label_visibility="hidden", key="chat_input"
        )
    with col_send:
        send_clicked = st.button("Send →", use_container_width=True)

    if send_clicked and user_input.strip():
        # Re-check limit before sending
        can_send, _, _ = check_message_limit(st.session_state.uid)
        
        if not can_send:
            st.error("❌ You've reached your message limit. Please upgrade to Premium.")
            return
        
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        track_message(st.session_state.uid)

        # Call RAG chain with timing
        start_t = time.time()
        
        chain = st.session_state.rag_chain
        
        if chain:
            # ✅ Modern LCEL call
            result = chain.invoke({"question": user_input.strip()})
            
            # ✅ Ensure reply is string
            if isinstance(result, dict):
                reply = result.get("answer") or result.get("output") or str(result)
            else:
                reply = str(result)
            
            sources = []
        
        else:
            # Fallback to direct LLM (no knowledge base) - UPGRADED
            prompt = user_input.strip()
            
            groq_api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.3,  # Lower temp for more focused responses
                max_tokens=4096,  # Higher token limit for detailed answers
                groq_api_key=groq_api_key
            )
            
            result = llm.invoke(prompt)
            reply = result.content if hasattr(result, "content") else str(result)
            sources = []
        
        # ✅ Track response time
        elapsed_ms = int((time.time() - start_t) * 1000)
        track_response_time(st.session_state.uid, elapsed_ms, success=True)
        
        # ✅ Append assistant reply
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": reply,
            "sources": sources
        })
        
        # ✅ Satisfaction rating prompt (every 10 messages)
        if len(st.session_state.chat_history) % 10 == 0:
            st.markdown("---")
            st.markdown("**How was that response?**")
            cols = st.columns(5)
            
            for i, col in enumerate(cols, 1):
                with col:
                    if st.button(f"{'⭐' * i}", key=f"rating_{i}_{len(st.session_state.chat_history)}"):
                        track_rating(st.session_state.uid, i)
                        st.success("Thanks for the feedback!")



    # Document upload (with limit check)
    st.divider()
    with st.expander("📄 Upload a document to add to knowledge base"):
        can_upload, docs_remaining, docs_limit = check_document_limit(st.session_state.uid)
        
        if plan == "free":
            st.caption(f"📊 Documents remaining: **{docs_remaining}/{docs_limit}**")
        
        if not can_upload:
            st.warning("❌ You've reached your document upload limit (10 documents). Upgrade to Premium for unlimited uploads!")
            if st.button("⭐ Upgrade to Premium", use_container_width=True):
                checkout_url = create_checkout_session(st.session_state.uid, st.session_state.email)
                if checkout_url:
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={checkout_url}">', unsafe_allow_html=True)
        else:
            uploaded = st.file_uploader("Upload .txt or .pdf", type=["txt", "pdf"], label_visibility="hidden")
            if uploaded:
                track_document_upload(st.session_state.uid)
                # In production: parse and add to vector store
                st.success(f"Uploaded: **{uploaded.name}** — tracked successfully.")
                st.info("💡 To add this to the knowledge base, append its content to `knowledge.txt` and rebuild the vector store.")


# ─────────────────────────────────────────────
# User Dashboard (NEW)
# ─────────────────────────────────────────────
def render_user_dashboard():
    """Personal dashboard showing user's own usage statistics."""
    uid = st.session_state.uid
    user_data = get_user_data(uid)
    
    if not user_data:
        st.error("Could not load user data")
        return
    
    plan = user_data.get("plan", "free")
    messages_sent = user_data.get("messages_sent", 0)
    docs_uploaded = user_data.get("docs_uploaded", 0)
    limits = user_data.get("limits", FREE_PLAN_LIMITS)
    
    # Header
    st.markdown(f"## 📊 My Dashboard")
    st.caption(f"Welcome back, **{user_data.get('full_name', 'User')}**!")
    
    st.divider()
    
    # Plan status
    col_plan, col_upgrade = st.columns([2, 1])
    with col_plan:
        if plan == "premium":
            st.markdown("""
            <div class="metric-card user">
                <div class="label">Current Plan</div>
                <div class="value">⭐ Premium</div>
                <div class="change"><span class="up">Unlimited usage</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card user">
                <div class="label">Current Plan</div>
                <div class="value">Free</div>
                <div class="change"><span class="down">Limited features</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_upgrade:
        if plan == "free":
            if st.button("⭐ Upgrade to Premium", use_container_width=True, key="upgrade_dashboard"):
                checkout_url = create_checkout_session(uid, st.session_state.email)
                if checkout_url:
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={checkout_url}">', unsafe_allow_html=True)
    
    # Usage statistics
    st.markdown('<div class="section-title">📈 Your Usage Statistics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if plan == "premium":
            usage_text = f"{messages_sent:,} messages sent"
        else:
            msgs_remaining = limits["messages"] - messages_sent
            usage_text = f"{msgs_remaining} remaining"
        
        st.markdown(f"""
        <div class="metric-card usage">
            <div class="label">Messages</div>
            <div class="value">{messages_sent:,}</div>
            <div class="change"><span class="{'up' if plan == 'premium' else 'down'}">{usage_text}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if plan == "premium":
            upload_text = f"{docs_uploaded:,} documents uploaded"
        else:
            docs_remaining = limits["documents"] - docs_uploaded
            upload_text = f"{docs_remaining} remaining"
        
        st.markdown(f"""
        <div class="metric-card usage">
            <div class="label">Documents</div>
            <div class="value">{docs_uploaded:,}</div>
            <div class="change"><span class="{'up' if plan == 'premium' else 'down'}">{upload_text}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Plan comparison (if on free plan)
    if plan == "free":
        st.markdown('<div class="section-title">🚀 Unlock More with Premium</div>', unsafe_allow_html=True)
        
        col_free, col_premium = st.columns(2)
        
        with col_free:
            st.markdown("""
            **Free Plan** (Current)
            - ✅ 100 messages
            - ✅ 10 documents
            - ✅ Basic support
            """)
        
        with col_premium:
            st.markdown("""
            **Premium Plan** ($9.99/mo)
            - 🚀 **Unlimited** messages
            - 🚀 **Unlimited** documents
            - 🚀 Priority support
            - 🚀 Advanced features
            - 🚀 No ads
            """)
        
        if st.button("⭐ Get Premium Now - $9.99/month", use_container_width=True, key="upgrade_comparison"):
            checkout_url = create_checkout_session(uid, st.session_state.email)
            if checkout_url:
                st.markdown(f'<meta http-equiv="refresh" content="0; url={checkout_url}">', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Admin Dashboard (UPDATED - admin only access)
# ─────────────────────────────────────────────
def render_admin_dashboard():
    """Admin analytics dashboard - ADMIN ACCESS ONLY."""
    # Check if user is admin
    if st.session_state.role != "admin":
        st.error("🚫 Access Denied: Admin privileges required")
        st.info("This dashboard is only accessible to administrators.")
        return
    
    uid = st.session_state.uid

    # ── Time-range selector ──
    col_title, col_range = st.columns([3, 1])
    with col_title:
        st.markdown("## 🎛️ Admin Analytics Dashboard", unsafe_allow_html=False)
    with col_range:
        time_range = st.selectbox(
            "Time Range", ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
            label_visibility="hidden"
        )

    range_map = {
        "Last 7 days":  7,
        "Last 30 days": 30,
        "Last 90 days": 90,
        "All time":     9999,
    }
    days = range_map[time_range]
    since = datetime.now(pytz.utc) - timedelta(days=days) if days < 9999 else None

    # ── Fetch data ──
    all_users      = get_all_users()
    usage_logs     = get_usage_logs(since)
    perf_logs      = get_performance_logs(since)
    ratings_data   = get_ratings(since)

    now_utc  = datetime.now(pytz.utc)
    seven_d  = now_utc - timedelta(days=7)
    thirty_d = now_utc - timedelta(days=30)

    # ─── Compute metrics ───
    total_users = len(all_users)
    active_7  = sum(1 for u in all_users if u.get("last_active") and u["last_active"] >= seven_d)
    active_30 = sum(1 for u in all_users if u.get("last_active") and u["last_active"] >= thirty_d)
    new_users_period = sum(
        1 for u in all_users
        if u.get("created_at") and u["created_at"] >= (since or datetime.min.replace(tzinfo=pytz.utc))
    )
    growth_rate = (new_users_period / max(total_users - new_users_period, 1)) * 100

    churn_count = sum(
        1 for u in all_users
        if u.get("last_active")
        and u["last_active"] < seven_d
        and u["last_active"] >= thirty_d
    )
    churn_rate = (churn_count / max(active_30, 1)) * 100

    msg_events  = [e for e in usage_logs if e.get("event") == "message_sent"]
    doc_events  = [e for e in usage_logs if e.get("event") == "document_uploaded"]
    total_msgs  = len(msg_events)
    total_docs  = len(doc_events)
    avg_msgs    = total_msgs / max(total_users, 1)
    avg_docs    = total_docs / max(total_users, 1)

    hour_counts = [0] * 24
    for e in msg_events:
        ts = e.get("timestamp")
        if ts:
            hour_counts[ts.hour] += 1
    peak_hour = hour_counts.index(max(hour_counts)) if any(hour_counts) else 0

    premium_users  = sum(1 for u in all_users if u.get("plan") == "premium")
    free_users     = total_users - premium_users
    MONTHLY_PRICE  = 9.99
    MRR            = premium_users * MONTHLY_PRICE
    conversion_rate = (premium_users / max(total_users, 1)) * 100
    ARPU           = MRR / max(total_users, 1)
    avg_months_active = 3
    LTV = avg_months_active * MONTHLY_PRICE

    if perf_logs:
        response_times = [p["response_time_ms"] for p in perf_logs]
        avg_response   = sum(response_times) / len(response_times)
        success_count  = sum(1 for p in perf_logs if p.get("success"))
        success_rate   = (success_count / len(perf_logs)) * 100
        error_rate     = 100 - success_rate
    else:
        avg_response = 0; success_rate = 0; error_rate = 0

    if ratings_data:
        avg_satisfaction = sum(r["rating"] for r in ratings_data) / len(ratings_data)
    else:
        avg_satisfaction = 0

    # ─────────────────────────────────────────────
    # 1. USER METRICS
    # ─────────────────────────────────────────────
    st.markdown('<div class="section-title">👥 User Metrics</div>', unsafe_allow_html=True)
    cols = st.columns(4)

    def _card(col, css_class, label, value, change_text, change_dir="up"):
        arrow = "↑" if change_dir == "up" else "↓"
        span_cls = change_dir
        with col:
            st.markdown(f"""
            <div class="metric-card {css_class}">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                <div class="change"><span class="{span_cls}">{arrow} {change_text}</span></div>
            </div>
            """, unsafe_allow_html=True)

    _card(cols[0], "user", "Total Users",      f"{total_users:,}",           f"{new_users_period} new", "up")
    _card(cols[1], "user", "Active (7 days)",  f"{active_7:,}",              f"{active_7/max(total_users,1)*100:.0f}% of total", "up")
    _card(cols[2], "user", "Churn Rate",       f"{churn_rate:.1f}%",         f"{churn_count} users churned", "down" if churn_rate > 0 else "up")
    _card(cols[3], "user", "Growth Rate",      f"{growth_rate:.1f}%",        f"vs previous period", "up" if growth_rate > 0 else "down")

    # ─────────────────────────────────────────────
    # 2. USAGE METRICS
    # ─────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Usage Metrics</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    _card(cols[0], "usage", "Total Messages",      f"{total_msgs:,}",   f"in {time_range.lower()}", "up")
    _card(cols[1], "usage", "Avg Msgs / User",     f"{avg_msgs:.1f}",   "per user", "up")
    _card(cols[2], "usage", "Total Docs Uploaded", f"{total_docs:,}",   f"in {time_range.lower()}", "up")
    _card(cols[3], "usage", "Avg Docs / User",     f"{avg_docs:.2f}",   "per user", "up")

    st.markdown("**Peak Usage by Hour (UTC)**", unsafe_allow_html=False)
    import pandas as pd
    hour_df = pd.DataFrame({
        "Hour": [f"{h:02d}:00" for h in range(24)],
        "Messages": hour_counts
    })
    st.bar_chart(hour_df.set_index("Hour"), color="#6366f1", height=220)
    st.caption(f"🔔 Peak hour: **{peak_hour:02d}:00 UTC** ({max(hour_counts)} messages)")

    # ─────────────────────────────────────────────
    # 3. REVENUE METRICS
    # ─────────────────────────────────────────────
    st.markdown('<div class="section-title">💰 Revenue Metrics</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    _card(cols[0], "rev", "MRR",               f"${MRR:,.2f}",           f"{premium_users} premium", "up")
    _card(cols[1], "rev", "Conversion Rate",  f"{conversion_rate:.1f}%", f"{premium_users}/{total_users}", "up")
    _card(cols[2], "rev", "ARPU",             f"${ARPU:.2f}",            "per user / mo", "up")
    _card(cols[3], "rev", "Est. LTV",         f"${LTV:.2f}",             f"avg {avg_months_active} mo", "up")

    col_pie1, col_pie2 = st.columns([1, 2])
    with col_pie1:
        pie_df = pd.DataFrame({
            "Plan": ["Free", "Premium"],
            "Users": [free_users, premium_users]
        })
        st.pyplot(_pie_chart(pie_df), use_container_width=True)
    with col_pie2:
        st.markdown("**Plan Distribution**")
        st.markdown(f"""
        | Plan    | Users | Percentage |
        |---------|-------|------------|
        | Free    | {free_users:,} | {free_users/max(total_users,1)*100:.1f}% |
        | Premium | {premium_users:,} | {premium_users/max(total_users,1)*100:.1f}% |
        """)

    # ─────────────────────────────────────────────
    # 4. PERFORMANCE METRICS
    # ─────────────────────────────────────────────
    st.markdown('<div class="section-title">⚡ Performance Metrics</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    _card(cols[0], "perf", "Avg Response Time",  f"{avg_response:.0f} ms",       f"{len(perf_logs)} requests", "up" if avg_response < 2000 else "down")
    _card(cols[1], "perf", "Success Rate",       f"{success_rate:.1f}%",         f"{sum(1 for p in perf_logs if p.get('success'))} ok", "up")
    _card(cols[2], "perf", "Error Rate",         f"{error_rate:.1f}%",           f"{sum(1 for p in perf_logs if not p.get('success'))} errors", "down" if error_rate > 0 else "up")
    _card(cols[3], "perf", "Avg Satisfaction",   f"{avg_satisfaction:.1f} / 5",  f"{len(ratings_data)} ratings", "up" if avg_satisfaction >= 3.5 else "down")

    if perf_logs:
        perf_df = pd.DataFrame(perf_logs).sort_values("timestamp")
        perf_df["idx"] = range(len(perf_df))
        st.markdown("**Response Time Trend (ms)**")
        st.line_chart(
            perf_df.set_index("idx")[["response_time_ms"]],
            color="#fb923c",
            height=200,
        )

    # ─────────────────────────────────────────────
    # 5. Recent Activity
    # ─────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Recent Activity</div>', unsafe_allow_html=True)
    recent = sorted(usage_logs, key=lambda x: x.get("timestamp", datetime.min.replace(tzinfo=pytz.utc)), reverse=True)[:15]
    if recent:
        rows = ""
        for entry in recent:
            ts   = entry.get("timestamp", "—")
            evt  = entry.get("event", "—")
            uid_short = entry.get("uid", "—")[:8] + "…"
            rows += f"<tr><td>{ts.strftime('%Y-%m-%d %H:%M') if hasattr(ts,'strftime') else ts}</td><td>{uid_short}</td><td>{evt}</td></tr>"

        st.markdown(f"""
        <table class="dash-table">
            <thead><tr><th>Timestamp</th><th>User</th><th>Event</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.info("No activity data yet in the selected range.")


def _pie_chart(df):
    """Return a matplotlib pie figure for plan distribution."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    colors = ["#6366f1", "#34d399"]
    ax.pie(
        df["Users"],
        labels=df["Plan"],
        autopct="%1.0f%%",
        colors=colors,
        startangle=140,
        textprops={"color": "#cbd5e1", "fontsize": 11},
    )
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────
# Main Router
# ─────────────────────────────────────────────
if not st.session_state.authenticated:
    render_auth()
elif st.session_state.page == "user_dashboard":
    render_user_dashboard()
elif st.session_state.page == "admin_dashboard":
    render_admin_dashboard()
else:
    render_chat()