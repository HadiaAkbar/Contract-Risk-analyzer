import streamlit as st
import os
from summarizer import read_file, generate_txt_bytes, generate_pdf_bytes, generate_combined_txt_bytes, generate_pdf_bytes_multi
from ai_analyzer import AIAnalyzer
from database import SessionLocal, User, Document, get_db
from sqlalchemy.orm import Session
from typing import List, Dict, Any

st.set_page_config(
    page_title="Contract Analyzer — AI-Powered Risk Assessment",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS based on the provided design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --bg: #05170f;
        --bg-2: #071f14;
        --green-1: #0f6b45;
        --green-2: #17a75f;
        --green-3: #34d980;
        --green-glow: #22c76e;
        --text: #eafff3;
        --text-soft: #b6d9c6;
        --line: rgba(255,255,255,0.08);
        --panel: #0a2318;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text);
        background-color: var(--bg) !important;
    }

    /* Auth Page Specifics */
    .auth-container {
        display: flex;
        min-height: 80vh;
        background: linear-gradient(180deg, #04140d 0%, #061a11 100%);
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid var(--line);
    }

    .auth-panel {
        width: 420px;
        background: linear-gradient(180deg, #08201548 0%, #05170f 100%), var(--bg-2);
        border-right: 1px solid var(--line);
        padding: 40px;
        display: flex;
        flex-direction: column;
    }

    .auth-hero {
        flex: 1;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 60px;
        overflow: hidden;
    }

    .logo-text {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 20px;
        font-weight: 800;
        color: #fff;
        margin-bottom: 40px;
    }

    .auth-heading {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-soft);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 18px;
    }

    /* Buttons & Inputs */
    .stButton>button {
        width: 100%;
        background: linear-gradient(180deg, var(--green-3), var(--green-2)) !important;
        color: #04170e !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 0 !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 24px -8px rgba(34,199,110,0.4) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
    }

    .stTextInput>div>div>input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
        color: #fff !important;
        padding: 12px !important;
    }

    .stTextInput>div>div>input:focus {
        border-color: var(--green-3) !important;
        background: rgba(52,217,128,0.06) !important;
    }

    /* Hero Copy */
    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 600;
        color: var(--green-3);
        text-transform: uppercase;
        background: rgba(52,217,128,0.08);
        border: 1px solid rgba(52,217,128,0.25);
        padding: 7px 14px;
        border-radius: 999px;
        margin-bottom: 20px;
    }

    h1 {
        font-size: 40px;
        font-weight: 800;
        line-height: 1.2;
        color: #fff;
        margin-bottom: 20px;
    }

    h1 span {
        background: linear-gradient(180deg, var(--green-3), var(--green-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-text {
        font-size: 16px;
        color: var(--text-soft);
        line-height: 1.6;
        max-width: 500px;
    }

    /* Main Workspace UI */
    .header-section { text-align: center; padding: 3rem 1rem; }
    .neu-panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .panel-green { border-left: 4px solid var(--green-3); }
    .panel-mint { border-left: 4px solid var(--green-glow); }
    
    .metric-card {
        background: var(--panel);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid var(--line);
    }
    .metric-label { font-size: 12px; color: var(--text-soft); text-transform: uppercase; }
    .metric-value { font-size: 32px; font-weight: 800; color: var(--green-3); }

    [data-testid="stSidebar"] {
        background-color: var(--bg-2) !important;
        border-right: 1px solid var(--line);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_ai_analyzer():
    return AIAnalyzer()

ai_analyzer = get_ai_analyzer()

# --- User Authentication ---
def authenticate_user(username, password):
    db: Session = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if user and user.password_hash == password:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_id"] = user.id
        st.session_state["user_role"] = user.role
        return True
    return False

def register_user(username, password):
    db: Session = next(get_db())
    if db.query(User).filter(User.username == username).first():
        return False
    new_user = User(username=username, password_hash=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return True

def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["user_id"] = None
    st.session_state["user_role"] = None

# --- Application Logic ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    # Display the Auth Page
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("""
        <div class="logo-text">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 3v18l8-5 8 5V3a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1z" fill="#34d980"/>
            </svg>
            Contract Analyzer
        </div>
        <p class="auth-heading">Login / Register</p>
        """, unsafe_allow_html=True)
        
        auth_tab = st.radio("Select Action", ["Login", "Register"], label_visibility="collapsed")
        
        if auth_tab == "Login":
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if authenticate_user(username, password):
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            new_user = st.text_input("New Username", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Create Account"):
                if register_user(new_user, new_pass):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username taken")
                    
        st.markdown("""
        <div style="margin-top: 40px; font-size: 12px; color: #b6d9c6; opacity: 0.6;">
            By continuing you agree to our <span style="color: #34d980">Terms</span> and <span style="color: #34d980">Privacy Policy</span>.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="auth-hero">
            <div class="hero-copy">
                <div class="eyebrow">AI-Powered</div>
                <h1>Welcome to the <span>Contract & Legal Document Risk Analyzer</span></h1>
                <p class="hero-text">Upload any agreement and we'll flag termination windows, auto-renewals, and liability exposure in seconds.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # --- Main Workspace ---
    with st.sidebar:
        st.markdown("<div class=\"logo-text\">Contract Analyzer AI</div>", unsafe_allow_html=True)
        st.write(f"Logged in as: **{st.session_state['username']}**")
        choice = st.selectbox("WORKSPACE", ["Document Analysis", "Semantic Search", "Dashboard", "Admin Panel"])
        if st.button("Logout"):
            logout_user()
            st.rerun()

    if choice == "Document Analysis":
        st.markdown("<div class=\"header-section\"><h1>Contract Analysis</h1><p class=\"tagline\">Upload documents to identify risks and key obligations.</p></div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Document", type=["txt", "pdf", "docx"])
        if uploaded_file:
            temp_file_path = os.path.join("temp_docs", uploaded_file.name)
            os.makedirs("temp_docs", exist_ok=True)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                document_content = read_file(temp_file_path)
                st.success("Document ready for analysis.")
                
                if st.button("Run AI Analysis"):
                    with st.spinner("Processing document..."):
                        analysis_result = ai_analyzer.analyze_document(document_content)
                        summary_result = ai_analyzer.summarize_document(document_content)
                        
                        db: Session = next(get_db())
                        new_doc = Document(
                            user_id=st.session_state["user_id"],
                            filename=uploaded_file.name,
                            content=document_content,
                            executive_summary=summary_result
                        )
                        db.add(new_doc)
                        db.commit()
                        
                        st.subheader("Analysis Results")
                        st.markdown(f'<div class="neu-panel panel-green">{analysis_result}</div>', unsafe_allow_html=True)
                        
                        st.subheader("Executive Summary")
                        st.markdown(f'<div class="neu-panel panel-mint">{summary_result}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

    elif choice == "Semantic Search":
        st.markdown("<div class=\"header-section\"><h1>Semantic Search</h1></div>", unsafe_allow_html=True)
        user_query = st.text_input("Ask a question about your documents:")
        if user_query and st.button("Search"):
            db: Session = next(get_db())
            user_docs = db.query(Document).filter(Document.user_id == st.session_state["user_id"]).all()
            if not user_docs:
                st.info("No documents found.")
            else:
                for doc in user_docs:
                    res = ai_analyzer.semantic_search(doc.content, user_query)
                    if res:
                        st.markdown(f"**From: {doc.filename}**")
                        st.markdown(f'<div class="neu-panel panel-green">{res}</div>', unsafe_allow_html=True)

    elif choice == "Dashboard":
        st.markdown("<div class=\"header-section\"><h1>Dashboard</h1></div>", unsafe_allow_html=True)
        db: Session = next(get_db())
        user_docs = db.query(Document).filter(Document.user_id == st.session_state["user_id"]).all()
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><p class="metric-label">Total Docs</p><p class="metric-value">{len(user_docs)}</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><p class="metric-label">Risks Flagged</p><p class="metric-value">0</p></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><p class="metric-label">Active Alerts</p><p class="metric-value">0</p></div>', unsafe_allow_html=True)

    elif choice == "Admin Panel":
        if st.session_state["user_role"] == "admin":
            st.subheader("System Administration")
            db: Session = next(get_db())
            users = db.query(User).all()
            for u in users:
                st.write(f"User: {u.username} | Role: {u.role}")
        else:
            st.error("Access Denied")
