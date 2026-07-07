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
    initial_sidebar_state="collapsed"
)

# --- Global State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- Aggressive CSS Overrides ---
auth_css = """
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

    /* Hide Streamlit elements on login */
    header, [data-testid="stSidebar"], [data-testid="stToolbar"] {
        display: none !important;
    }

    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        color: var(--text) !important;
        background-color: var(--bg) !important;
    }

    /* Auth Layout */
    .auth-wrapper {
        display: flex;
        min-height: 100vh;
        width: 100vw;
    }

    .auth-left {
        width: 420px;
        background: linear-gradient(180deg, #08201548 0%, #05170f 100%), var(--bg-2);
        border-right: 1px solid var(--line);
        padding: 60px 40px;
        display: flex;
        flex-direction: column;
        z-index: 10;
    }

    .auth-right {
        flex: 1;
        background: linear-gradient(180deg, #04140d 0%, #061a11 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }

    /* Logo & Headings */
    .logo-box {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 22px;
        font-weight: 800;
        color: #fff;
        margin-bottom: 56px;
    }

    .auth-tag {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-soft);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 24px;
    }

    /* Streamlit Input & Button Styling */
    .stTextInput label {
        color: var(--text-soft) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        margin-bottom: 8px !important;
    }

    .stTextInput div[data-baseweb="input"] {
        background-color: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
    }

    .stTextInput input {
        color: white !important;
        padding: 12px !important;
    }

    .stButton button {
        background: linear-gradient(180deg, var(--green-3), var(--green-2)) !important;
        color: #04170e !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px !important;
        width: 100% !important;
        box-shadow: 0 10px 24px -8px rgba(34,199,110,0.5) !important;
        margin-top: 10px !important;
    }

    /* Hero Section Content */
    .hero-content {
        text-align: center;
        max-width: 600px;
        padding: 40px;
        z-index: 5;
    }

    .eyebrow-pill {
        display: inline-block;
        padding: 6px 14px;
        background: rgba(52,217,128,0.1);
        border: 1px solid rgba(52,217,128,0.2);
        border-radius: 100px;
        color: var(--green-3);
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        line-height: 1.1;
        color: white;
        margin-bottom: 20px;
    }

    .hero-title span {
        background: linear-gradient(180deg, var(--green-3), var(--green-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-desc {
        font-size: 17px;
        color: var(--text-soft);
        line-height: 1.6;
    }

    /* Orbs for Background */
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
    }
    .orb-1 { width: 400px; height: 400px; background: rgba(52,217,128,0.2); top: -100px; right: -100px; }
    .orb-2 { width: 300px; height: 300px; background: rgba(23,167,95,0.15); bottom: -50px; left: -50px; }
</style>
"""

workspace_css = """
<style>
    /* Restore sidebar for workspace */
    [data-testid="stSidebar"] {
        display: flex !important;
        background-color: #071f14 !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    header { display: flex !important; }
    
    .main .block-container {
        padding: 3rem 5rem !important;
    }

    .neu-panel {
        background: #0a2318;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        border-left: 4px solid #34d980;
    }

    .metric-card {
        background: #0a2318;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    .metric-label { font-size: 12px; color: #b6d9c6; text-transform: uppercase; }
    .metric-value { font-size: 36px; font-weight: 800; color: #34d980; }
</style>
"""

@st.cache_resource
def get_ai_analyzer():
    return AIAnalyzer()

ai_analyzer = get_ai_analyzer()

# --- Auth Functions ---
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

# --- Main App ---
if not st.session_state["logged_in"]:
    st.markdown(auth_css, unsafe_allow_html=True)
    
    # Use HTML for the structure
    st.markdown("""
    <div class="auth-wrapper">
        <div class="auth-left" id="auth-form-container">
        </div>
        <div class="auth-right">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="hero-content">
                <div class="eyebrow-pill">AI-Powered</div>
                <div class="hero-title">Welcome to the<br><span>Contract & Legal<br>Document Risk Analyzer</span></div>
                <p class="hero-desc">Upload any agreement and we'll flag termination windows, auto-renewals, and liability exposure in seconds.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inject the actual Streamlit widgets into the "auth-left" area using columns
    # We use a placeholder-like approach by positioning the widgets over the left panel
    with st.container():
        c1, c2 = st.columns([420, 1000]) # Match the 420px width
        with c1:
            st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True) # Spacer for logo
            st.markdown("""
            <div class="logo-box">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                    <path d="M4 3v18l8-5 8 5V3a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1z" fill="#34d980"/>
                </svg>
                Contract Analyzer
            </div>
            <div class="auth-tag">Login / Register</div>
            """, unsafe_allow_html=True)
            
            mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed")
            
            if mode == "Login":
                u = st.text_input("Username", key="l_u")
                p = st.text_input("Password", type="password", key="l_p")
                if st.button("Login"):
                    if authenticate_user(u, p):
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            else:
                u = st.text_input("New Username", key="r_u")
                p = st.text_input("New Password", type="password", key="r_p")
                if st.button("Create Account"):
                    if register_user(u, p):
                        st.success("Account created!")
                    else:
                        st.error("Username exists")

            st.markdown("""
            <div style="margin-top: auto; padding-top: 40px; font-size: 12px; color: #b6d9c6; opacity: 0.6;">
                By continuing you agree to our <span style="color: #34d980">Terms</span> and <span style="color: #34d980">Privacy Policy</span>.
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown(workspace_css, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("<div style='font-size: 20px; font-weight: 800; color: white; margin-bottom: 20px;'>Contract Analyzer AI</div>", unsafe_allow_html=True)
        st.write(f"Logged in: **{st.session_state['username']}**")
        choice = st.selectbox("WORKSPACE", ["Document Analysis", "Semantic Search", "Dashboard"])
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

    if choice == "Document Analysis":
        st.title("Contract Analysis")
        uploaded_file = st.file_uploader("Upload Agreement", type=["pdf", "docx", "txt"])
        if uploaded_file:
            st.success("File uploaded.")
            if st.button("Analyze"):
                with st.spinner("AI is reading..."):
                    # Mock logic for brevity
                    st.markdown('<div class="neu-panel"><h3>Analysis Summary</h3><p>The AI has identified 3 high-risk clauses regarding termination and liability.</p></div>', unsafe_allow_html=True)

    elif choice == "Dashboard":
        st.title("Dashboard")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown('<div class="metric-card"><div class="metric-label">Total Docs</div><div class="metric-value">12</div></div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="metric-card"><div class="metric-label">High Risk</div><div class="metric-value">3</div></div>', unsafe_allow_html=True)
        with c3: st.markdown('<div class="metric-card"><div class="metric-label">Pending Review</div><div class="metric-value">5</div></div>', unsafe_allow_html=True)
