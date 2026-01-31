import os
import gradio as gr
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# Import Firebase functions
from firebase_config import (
    signup_user, login_user, get_user_data,
    update_message_count, update_document_count,
    check_message_quota, check_document_quota
)

# Load environment variables
load_dotenv()

# ======================================================
# 🔐 ENVIRONMENT
# ======================================================
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("Missing GROQ_API_KEY in environment variables")

os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "APEX-RAG-Chatbot")

# ======================================================
# 🧠 LLM — LLAMA 3.3 70B
# ======================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.6,
    streaming=True
)

# ======================================================
# 📦 GLOBAL VECTOR STORE
# ======================================================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Global storage for user sessions
user_vectorstores = {}
user_retrievers = {}

# ======================================================
# 📄 DOCUMENT INGESTION (WITH QUOTA CHECK)
# ======================================================
def ingest_files(files, user_id):
    if not user_id:
        return "❌ Please login first."
    
    if not files:
        return "❌ Please upload at least one file."
    
    # Check document quota
    if not check_document_quota(user_id):
        user_data = get_user_data(user_id)
        return f"❌ Document limit reached ({user_data['documents_used']}/{user_data['documents_limit']}). Upgrade to upload more!"
    
    try:
        all_docs = []
        
        for file in files:
            file_path = file.name
            
            if file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
            else:
                continue
            
            docs = loader.load()
            all_docs.extend(docs)
        
        if not all_docs:
            return "❌ No valid documents found."
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        chunks = splitter.split_documents(all_docs)
        
        vectorstore = FAISS.from_documents(chunks, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Store in user-specific storage
        user_vectorstores[user_id] = vectorstore
        user_retrievers[user_id] = retriever
        
        # Update document count
        update_document_count(user_id)
        
        user_data = get_user_data(user_id)
        return f"✅ Successfully indexed {len(chunks)} chunks from {len(files)} file(s). Documents: {user_data['documents_used']}/{user_data['documents_limit']}"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ======================================================
# 🧩 PROMPT (RAG + MEMORY)
# ======================================================
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are APEX, an intelligent AI assistant. "
     "Answer questions based on the provided context. "
     "If you don't know, say so clearly."),
    ("human",
     "Context:\n{context}\n\n"
     "Chat History:\n{history}\n\n"
     "Question: {question}")
])

chain = prompt | llm | StrOutputParser()

# ======================================================
# ⚡ STREAMING CHAT FUNCTION (WITH QUOTA CHECK)
# ======================================================
def chat(message, history, user_id):
    if not user_id:
        history.append({
            "role": "assistant",
            "content": "⚠️ Please login to use the chat."
        })
        return history, ""
    
    if not message or not message.strip():
        return history, ""
    
    # Check message quota
    if not check_message_quota(user_id):
        user_data = get_user_data(user_id)
        history.append({
            "role": "assistant",
            "content": f"⚠️ Message limit reached ({user_data['messages_used']}/{user_data['messages_limit']}). Upgrade for more!"
        })
        return history, ""
    
    retriever = user_retrievers.get(user_id)
    
    if retriever is None:
        history.append({
            "role": "assistant",
            "content": "⚠️ Please upload and index documents first."
        })
        return history, ""
    
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": ""})
    
    try:
        docs = retriever.invoke(message)
        context = "\n\n".join(d.page_content for d in docs)
        
        chat_history = "\n".join(
            f"{m['role'].capitalize()}: {m['content']}"
            for m in history[:-1][-6:]
        )
        
        response = ""
        for token in chain.stream({
            "context": context,
            "history": chat_history,
            "question": message
        }):
            response += token
            history[-1]["content"] = response
            yield history, ""
        
        # Update message count after successful response
        update_message_count(user_id)
        
    except Exception as e:
        history[-1]["content"] = f"❌ Error: {str(e)}"
        yield history, ""

# ======================================================
# 🎨 CUSTOM CSS - ULTRA MODERN
# ======================================================
custom_css = """
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --bg: #0f172a;
    --surface: #1e293b;
    --surface-light: #334155;
    --text: #f8fafc;
    --text-muted: #94a3b8;
    --border: #334155;
    --success: #10b981;
    --error: #ef4444;
}
* {
    font-family: 'Inter', -apple-system, sans-serif;
}
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    background: var(--bg) !important;
}
.auth-logo {
    text-align: center;
    margin-bottom: 2rem;
}
.auth-logo h1 {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.auth-logo p {
    color: var(--text-muted);
    margin-top: 0.5rem;
    font-size: 0.95rem;
}
.auth-input {
    background: var(--bg) !important;
    border: 2px solid var(--border) !important;
    color: var(--text) !important;
    padding: 0.875rem !important;
    border-radius: 12px !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
}
.auth-input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
    outline: none !important;
}
.auth-button {
    width: 100%;
    padding: 1rem !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    margin-top: 1.5rem !important;
}
.auth-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
}
.auth-switch {
    text-align: center;
    margin-top: 1.5rem;
    color: var(--text-muted);
}
.auth-switch button {
    background: transparent !important;
    border: none !important;
    color: var(--primary-light) !important;
    cursor: pointer !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
.auth-switch button:hover {
    background: var(--surface-light) !important;
}
.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}
.dashboard-title {
    font-size: 2rem;
    font-weight: 800;
    color: white;
    margin: 0;
}
.dashboard-subtitle {
    color: rgba(255,255,255,0.8);
    margin-top: 0.5rem;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.25rem;
    margin: 2rem 0;
}
.stat-card {
    background: var(--surface);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid var(--border);
    transition: transform 0.2s ease;
}
.stat-card:hover {
    transform: translateY(-4px);
    border-color: var(--primary);
}
.stat-label {
    color: var(--text-muted);
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}
.stat-value {
    color: var(--text);
    font-size: 1.75rem;
    font-weight: 700;
}
.stat-bar {
    height: 6px;
    background: var(--bg);
    border-radius: 3px;
    margin-top: 0.75rem;
    overflow: hidden;
}
.stat-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 3px;
    transition: width 0.5s ease;
}
.section-title {
    text-align: center;
    margin: 2rem 0 1rem;
}
.section-title h3 {
    color: var(--text);
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
}
.section-title p {
    color: var(--text-muted);
    margin-top: 0.5rem;
}
.upload-zone {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}
.upload-zone:hover {
    border-color: var(--primary);
    background: var(--surface-light);
}
.primary-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.875rem 2rem !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
}
.secondary-btn {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 2px solid var(--border) !important;
    padding: 0.875rem 2rem !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.secondary-btn:hover {
    border-color: var(--primary) !important;
    background: var(--surface-light) !important;
}
.chat-container {
    background: var(--surface);
    border-radius: 20px;
    border: 1px solid var(--border);
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.animate {
    animation: slideIn 0.4s ease-out;
}
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
}
"""

# ======================================================
# ✅ MODERN AUTH + DASHBOARD
# ======================================================
with gr.Blocks(css=custom_css, theme=gr.themes.Default()) as demo:
    
    user_id_state = gr.State(None)
    
    # ============ LOGIN PANEL ============
    with gr.Column(visible=True, elem_classes="animate") as login_panel:
        gr.HTML("""
        <div class="auth-logo">
            <h1>⚡ APEX</h1>
            <p>Welcome back! Sign in to continue</p>
        </div>
        """)
        
        email_login = gr.Textbox(
            label="Email Address",
            placeholder="your.email@example.com",
            elem_classes="auth-input"
        )
        password_login = gr.Textbox(
            label="Password",
            placeholder="Enter your password",
            type="password",
            elem_classes="auth-input"
        )
        
        login_btn = gr.Button("Sign In", elem_classes="auth-button")
        login_msg = gr.Textbox(label="", interactive=False, show_label=False)
        
        gr.HTML("""
        <div class="auth-switch">
            <span>Don't have an account?</span>
        </div>
        """)
        
        switch_to_signup = gr.Button("Create Free Account", elem_classes="auth-switch")
    
    # ============ SIGNUP PANEL ============
    with gr.Column(visible=False, elem_classes="animate") as signup_panel:
        gr.HTML("""
        <div class="auth-logo">
            <h1>⚡ APEX</h1>
            <p>Create your free account</p>
        </div>
        """)
        
        name_signup = gr.Textbox(
            label="Full Name",
            placeholder="John Doe",
            elem_classes="auth-input"
        )
        email_signup = gr.Textbox(
            label="Email Address",
            placeholder="your.email@example.com",
            elem_classes="auth-input"
        )
        password_signup = gr.Textbox(
            label="Password",
            placeholder="At least 6 characters",
            type="password",
            elem_classes="auth-input"
        )
        
        signup_btn = gr.Button("Create Account", elem_classes="auth-button")
        signup_msg = gr.Textbox(label="", interactive=False, show_label=False)
        
        gr.HTML("""
        <div class="auth-switch">
            <span>Already have an account?</span>
        </div>
        """)
        
        switch_to_login = gr.Button("Sign In Instead", elem_classes="auth-switch")
    
    # ============ MAIN DASHBOARD ============
    with gr.Column(visible=False) as main_panel:
        
        # Dynamic header
        header_html = gr.HTML("")
        
        # Usage stats
        stats_html = gr.HTML("")
        
        # Upload Section
        gr.HTML("""
        <div class="section-title">
            <h3>📚 Knowledge Base</h3>
            <p>Upload documents to chat with them using AI</p>
        </div>
        """)
        
        file_upload = gr.File(
            file_types=[".pdf", ".txt"],
            file_count="multiple",
            label="Drop files here or click to browse",
            elem_classes="upload-zone"
        )
        
        ingest_btn = gr.Button("🔄 Index Documents", elem_classes="primary-btn")
        status = gr.Textbox(show_label=False, interactive=False)
        
        # Chat Section
        gr.HTML("""
        <div class="section-title">
            <h3>💬 AI Assistant</h3>
            <p>Ask questions about your documents</p>
        </div>
        """)
        
        chatbot = gr.Chatbot(
            height=500,
            show_label=False,
            elem_classes="chat-container"
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask me anything about your documents...",
                show_label=False,
                scale=9
            )
            send = gr.Button("Send", scale=1, elem_classes="primary-btn")
        
        with gr.Row():
            clear = gr.Button("🗑️ Clear Chat", elem_classes="secondary-btn")
            logout_btn = gr.Button("🚪 Logout", elem_classes="secondary-btn")
    
    # ======================================================
    # 🔄 PANEL SWITCHING
    # ======================================================
    def show_signup():
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False)
        )
    
    def show_login():
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False)
        )
    
    switch_to_signup.click(
        show_signup,
        outputs=[login_panel, signup_panel, main_panel]
    )
    
    switch_to_login.click(
        show_login,
        outputs=[login_panel, signup_panel, main_panel]
    )
    
    # ======================================================
    # ✅ SIGNUP HANDLER
    # ======================================================
    def handle_signup(name, email, password):
        success, message, _ = signup_user(email, password, name)
        return message
    
    signup_btn.click(
        handle_signup,
        inputs=[name_signup, email_signup, password_signup],
        outputs=signup_msg
    )
    
    # ======================================================
    # ✅ LOGIN HANDLER
    # ======================================================
    def handle_login(email, password):
        success, message, user_id, token, user_data = login_user(email, password)
        
        if success:
            # Create header
            header = f"""
            <div class="dashboard-header animate">
                <div class="dashboard-title">⚡ APEX</div>
                <div class="dashboard-subtitle">
                    Welcome back, {user_data.get('name', 'User')}! • Free Plan
                </div>
            </div>
            """
            
            # Create stats
            msg_used = user_data.get('messages_used', 0)
            msg_limit = user_data.get('messages_limit', 50)
            doc_used = user_data.get('documents_used', 0)
            doc_limit = user_data.get('documents_limit', 3)
            
            msg_pct = (msg_used / msg_limit) * 100
            doc_pct = (doc_used / doc_limit) * 100
            
            stats = f"""
            <div class="stats-grid animate">
                <div class="stat-card">
                    <div class="stat-label">💬 Messages Used</div>
                    <div class="stat-value">{msg_used} / {msg_limit}</div>
                    <div class="stat-bar">
                        <div class="stat-bar-fill" style="width: {msg_pct}%"></div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">📁 Documents Uploaded</div>
                    <div class="stat-value">{doc_used} / {doc_limit}</div>
                    <div class="stat-bar">
                        <div class="stat-bar-fill" style="width: {doc_pct}%"></div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">⭐ Current Plan</div>
                    <div class="stat-value">Free</div>
                    <div style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--text-muted);">
                        Upgrade for unlimited access
                    </div>
                </div>
            </div>
            """
            
            return (
                message,
                user_id,
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
                header,
                stats
            )
        
        return message, None, gr.update(), gr.update(), gr.update(), "", ""
    
    login_btn.click(
        handle_login,
        inputs=[email_login, password_login],
        outputs=[login_msg, user_id_state, login_panel, signup_panel, main_panel, header_html, stats_html]
    )
    
    # ======================================================
    # 🚪 LOGOUT HANDLER
    # ======================================================
    def handle_logout():
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            "",
            "",
            []
        )
    
    logout_btn.click(
        handle_logout,
        outputs=[user_id_state, login_panel, signup_panel, main_panel, header_html, stats_html, chatbot]
    )
    
    # ======================================================
    # 💬 CHAT HANDLERS
    # ======================================================
    ingest_btn.click(
        ingest_files,
        inputs=[file_upload, user_id_state],
        outputs=status
    )
    
    send.click(chat, [msg, chatbot, user_id_state], [chatbot, msg])
    msg.submit(chat, [msg, chatbot, user_id_state], [chatbot, msg])
    clear.click(lambda: [], None, chatbot)

if __name__ == "__main__":
    # Production-ready launch configuration
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        share=False
    )
