import streamlit as st
import os
import datetime
from summarizer import read_file, generate_txt_bytes, generate_pdf_bytes, generate_combined_txt_bytes, generate_pdf_bytes_multi
from ai_analyzer import AIAnalyzer
from database import SessionLocal, User, Document, get_db
from sqlalchemy.orm import Session

# BUILD VERSION: 2026-07-07_v4.0 - FINAL NUCLEAR UI

st.set_page_config(
    page_title="Contract Analyzer AI",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Global State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- NUCLEAR CSS OVERRIDES ---
nuclear_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* 1. HIDE ALL DEFAULT ELEMENTS */
    header, [data-testid="stSidebar"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }

    /* 2. FORCE FULL SCREEN */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    .stApp {
        background-color: #0a1f16 !important;
        color: #eafff3 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 3. AUTH LAYOUT ENGINE */
    .nuclear-auth-container {
        display: flex;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #0a1f16;
    }

    .nuclear-left {
        width: 35%;
        background: linear-gradient(135deg, #0a1f16 0%, #0d2818 100%);
        border-right: 1px solid rgba(52,217,128,0.15);
        padding: 60px 50px;
        display: flex;
        flex-direction: column;
        z-index: 100;
        position: relative;
    }

    .nuclear-right {
        flex: 1;
        background: linear-gradient(135deg, #0a1f16 0%, #0d2818 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }

    /* 4. BACKGROUND ORBS - GLOWING EFFECT */
    .orb {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
        filter: blur(1px);
    }
    .orb-1 {
        width: 800px; height: 800px;
        right: -300px; top: -300px;
        background: radial-gradient(circle at 35% 30%, rgba(52,217,128,0.4), rgba(15,107,69,0.1) 50%, transparent 70%);
        box-shadow: 0 0 200px rgba(52,217,128,0.3);
    }
    .orb-2 {
        width: 600px; height: 600px;
        right: 100px; top: 150px;
        border: 2px solid rgba(52,217,128,0.2);
        background: radial-gradient(circle at 30% 25%, rgba(23,167,95,0.3), transparent 60%);
        box-shadow: inset 0 0 100px rgba(52,217,128,0.2), 0 0 150px rgba(52,217,128,0.15);
    }
    .orb-3 {
        width: 400px; height: 400px;
        right: 300px; top: 250px;
        border: 1px solid rgba(52,217,128,0.15);
        box-shadow: 0 0 80px rgba(52,217,128,0.1);
    }
    .orb-4 {
        width: 200px; height: 200px;
        left: 100px; bottom: 150px;
        border: 1px solid rgba(52,217,128,0.1);
        background: radial-gradient(circle at 35% 30%, rgba(23,167,95,0.15), transparent 60%);
        box-shadow: 0 0 60px rgba(52,217,128,0.08);
    }

    /* 5. DESIGN TOKENS */
    .logo-v2 {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 22px;
        font-weight: 800;
        color: #fff;
        margin-bottom: 80px;
    }
    .logo-v2 svg {
        width: 28px;
        height: 28px;
    }

    .auth-heading {
        font-size: 13px;
        font-weight: 600;
        color: #7a9d8f;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 0 0 24px;
    }

    .tabs {
        display: flex;
        gap: 8px;
        background: transparent;
        margin-bottom: 40px;
    }
    .tab {
        flex: 1;
        text-align: center;
        padding: 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: #7a9d8f;
        border-radius: 12px;
        cursor: pointer;
        transition: all .2s ease;
        user-select: none;
        background: transparent;
        border: 1px solid rgba(52,217,128,0.2);
    }
    .tab.active {
        background: linear-gradient(135deg, #34d980, #2bc970);
        color: #0a1f16;
        border-color: #34d980;
        box-shadow: 0 8px 24px rgba(52,217,128,0.3);
    }

    .field {
        margin-bottom: 24px;
    }
    .field label {
        display: block;
        font-size: 13px;
        font-weight: 600;
        color: #7a9d8f;
        margin-bottom: 10px;
        text-transform: capitalize;
    }
    .field input {
        width: 100%;
        background: rgba(52,217,128,0.05);
        border: 1px solid rgba(52,217,128,0.2);
        border-radius: 12px;
        padding: 14px 16px;
        font-size: 14px;
        font-family: 'Inter', sans-serif;
        color: #eafff3;
        outline: none;
        transition: all .2s ease;
    }
    .field input::placeholder {
        color: rgba(122,157,143,0.5);
    }
    .field input:focus {
        border-color: #34d980;
        background: rgba(52,217,128,0.08);
        box-shadow: 0 0 20px rgba(52,217,128,0.15);
    }

    .btn-login {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: linear-gradient(135deg, #34d980, #2bc970);
        color: #0a1f16;
        font-weight: 700;
        font-size: 15px;
        padding: 14px 0;
        border: none;
        border-radius: 12px;
        cursor: pointer;
        box-shadow: 0 12px 32px rgba(52,217,128,0.35);
        margin-top: 12px;
        font-family: 'Inter', sans-serif;
        transition: all .2s ease;
    }
    .btn-login:hover {
        filter: brightness(1.08);
        box-shadow: 0 16px 40px rgba(52,217,128,0.4);
        transform: translateY(-2px);
    }

    .auth-foot {
        margin-top: auto;
        padding-top: 40px;
        font-size: 12px;
        color: #7a9d8f;
        opacity: 0.8;
        line-height: 1.8;
    }
    .auth-foot a {
        color: #34d980;
        text-decoration: none;
        font-weight: 500;
        transition: color .2s ease;
    }
    .auth-foot a:hover {
        color: #2bc970;
    }

    /* HERO SECTION */
    .hero-v2 {
        text-align: center;
        max-width: 700px;
        z-index: 10;
        position: relative;
    }

    .pill-v2 {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        font-weight: 600;
        color: #34d980;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        background: rgba(52,217,128,0.1);
        border: 1px solid rgba(52,217,128,0.3);
        padding: 8px 16px;
        border-radius: 999px;
        margin-bottom: 40px;
    }
    .pill-v2::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #34d980;
        box-shadow: 0 0 12px #34d980;
    }

    h1.v2-title {
        font-size: 56px;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.02em;
        margin: 0 0 24px;
        color: #fff;
    }

    h1.v2-title span {
        background: linear-gradient(135deg, #34d980, #2bc970);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-v2 p {
        font-size: 16px;
        line-height: 1.8;
        color: #a8c9bc;
        max-width: 600px;
        margin: 0 auto;
    }

    /* 6. STREAMLIT WIDGET OVERRIDES */
    .stButton button {
        width: 100% !important;
        background: linear-gradient(135deg, #34d980, #2bc970) !important;
        color: #0a1f16 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 14px 0 !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 12px 32px rgba(52,217,128,0.35) !important;
        transition: all .2s ease !important;
    }
    .stButton button:hover {
        filter: brightness(1.08) !important;
        box-shadow: 0 16px 40px rgba(52,217,128,0.4) !important;
        transform: translateY(-2px) !important;
    }

    div[data-baseweb="input"] {
        background-color: rgba(52,217,128,0.05) !important;
        border: 1px solid rgba(52,217,128,0.2) !important;
        border-radius: 12px !important;
        transition: all .2s ease !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #34d980 !important;
        background-color: rgba(52,217,128,0.08) !important;
        box-shadow: 0 0 20px rgba(52,217,128,0.15) !important;
    }

    input {
        color: #eafff3 !important;
        font-size: 14px !important;
    }
    input::placeholder {
        color: rgba(122,157,143,0.5) !important;
    }

    /* Radio tabs styling */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        gap: 8px !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 40px !important;
    }
    div[data-testid="stRadio"] label {
        flex: 1 !important;
        text-align: center !important;
        padding: 12px 0 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #7a9d8f !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        transition: all .2s ease !important;
        background: transparent !important;
        border: 1px solid rgba(52,217,128,0.2) !important;
        display: block !important;
    }
    div[data-testid="stRadio"] label[data-selected="true"] {
        background: linear-gradient(135deg, #34d980, #2bc970) !important;
        color: #0a1f16 !important;
        border-color: #34d980 !important;
        box-shadow: 0 8px 24px rgba(52,217,128,0.3) !important;
    }
    div[data-testid="stRadio"] input {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > div {
        padding: 0 !important;
        margin: 0 !important;
        flex: 1 !important;
    }

    /* Error/Success messages */
    .stAlert {
        background: rgba(52,217,128,0.1) !important;
        border: 1px solid rgba(52,217,128,0.3) !important;
        border-radius: 12px !important;
    }

    /* Collapse button styling */
    .stButton[data-testid="baseButton-secondary"] button {
        background: transparent !important;
        color: #34d980 !important;
        border: 1px solid rgba(52,217,128,0.3) !important;
    }
</style>
"""

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

# --- Main Logic ---
if not st.session_state["logged_in"]:
    st.markdown(nuclear_css, unsafe_allow_html=True)
    
    # Force the layout structure
    st.markdown("""
    <div class="nuclear-auth-container">
        <div class="nuclear-left">
            <div class="logo-v2">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 3v18l8-5 8 5V3a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1z" fill="url(#grad)"/>
                    <defs>
                        <linearGradient id="grad" x1="4" y1="2" x2="20" y2="21" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#34d980"/>
                            <stop offset="1" stop-color="#0f6b45"/>
                        </linearGradient>
                    </defs>
                </svg>
                Contract Analyzer
            </div>
            
            <div class="auth-heading">Login / Register</div>
            
            <!-- Auth form anchor -->
            <div id="auth-anchor" style="flex: 1; display: flex; flex-direction: column;"></div>

            <div class="auth-foot">
                By continuing you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>.
            </div>
        </div>
        <div class="nuclear-right">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            <div class="orb orb-4"></div>

            <div class="hero-v2">
                <div class="pill-v2">AI-Powered</div>
                <h1 class="v2-title">Welcome to the <span>Contract & Legal<br>Document Risk Analyzer</span></h1>
                <p>Upload any agreement and we'll flag termination windows, auto-renewals, and liability exposure in seconds.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Place Streamlit widgets
    with st.container():
        st.markdown('<div style="position: absolute; top: 200px; left: 50px; width: calc(35% - 100px); z-index: 101;">', unsafe_allow_html=True)
        
        mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed")
        
        if mode == "Login":
            u = st.text_input("Username", key="u_login", placeholder="Enter your username")
            p = st.text_input("Password", type="password", key="p_login", placeholder="Enter your password")
            st.markdown('<div style="margin-top: 8px;">', unsafe_allow_html=True)
            if st.button("Login", use_container_width=True):
                if authenticate_user(u, p):
                    st.rerun()
                else:
                    st.error("Invalid login")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            u = st.text_input("Username", key="u_reg", placeholder="Choose a username")
            p = st.text_input("Password", type="password", key="p_reg", placeholder="Choose a password")
            st.markdown('<div style="margin-top: 8px;">', unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True):
                if register_user(u, p):
                    st.success("Account created!")
                else:
                    st.error("User exists")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Workspace UI
    st.markdown("<style>header {display: flex !important;} [data-testid='stSidebar'] {display: flex !important;}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.title("Contract AI")
        st.write(f"User: {st.session_state['username']}")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    st.title("Document Analysis")
    st.write("Welcome to your workspace.")
