import streamlit as st
import requests
import math

API_URL = st.secrets.get("API_URL", "http://localhost:8000") if hasattr(st, "secrets") else "http://localhost:8000"
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = "http://localhost:8000"

st.set_page_config(page_title="Contract Risk Analyzer", layout="wide", initial_sidebar_state="collapsed")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# Enhanced CSS with circular patterns and gauges
LOGIN_CSS = """
<style>
    * {box-sizing: border-box;}
    html, body {margin: 0; padding: 0;}
    
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    .stApp {
        background-color: #061109;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(52, 211, 153, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 90% 80%, rgba(34, 197, 94, 0.06) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(52, 211, 153, 0.03) 0%, transparent 70%);
        margin: 0; 
        padding: 0;
    }

    /* Circular decorative elements */
    .circular-accent {
        position: absolute;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(52, 211, 153, 0.1), transparent);
    }

    /* Animations */
    @keyframes cardEntranceLeft {
        0% {
            opacity: 0;
            transform: translateX(-100px) rotate(-5deg);
        }
        100% {
            opacity: 1;
            transform: translateX(0) rotate(0deg);
        }
    }
    
    @keyframes cardEntranceRight {
        0% {
            opacity: 0;
            transform: translateX(100px) rotate(5deg);
        }
        100% {
            opacity: 1;
            transform: translateX(0) rotate(0deg);
        }
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
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(52, 211, 153, 0.2); }
        50% { box-shadow: 0 0 40px rgba(52, 211, 153, 0.4); }
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes pulse-ring {
        0% {
            r: 45;
            opacity: 1;
        }
        100% {
            r: 65;
            opacity: 0;
        }
    }

    /* Main container layout */
    [data-testid="stHorizontalBlock"] {
        gap: 3rem !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh;
        margin: 0 !important;
        padding: 4rem 2rem !important;
        flex-wrap: wrap;
    }
    
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        display: flex !important;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* Left card - Credentials (High Visibility) */
    div[data-testid="column"]:has(> div .login-marker) {
        flex: 0 1 450px !important;
        max-width: 450px !important;
        animation: cardEntranceLeft 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"] {
        width: 100% !important;
        background: #0d1a13 !important;
        border: 2px solid #34d399 !important;
        border-radius: 28px;
        padding: 3rem 2.5rem !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"]::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.05) 0%, transparent 70%);
        pointer-events: none;
    }
    
    div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 60px -12px rgba(52, 211, 153, 0.3);
    }

    /* Right card - Welcome (High Visibility) */
    div[data-testid="column"]:has(> div .hero-marker) {
        flex: 0 1 450px !important;
        max-width: 450px !important;
        animation: cardEntranceRight 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"] {
        width: 100% !important;
        background: #071309 !important;
        border: 2px solid rgba(52, 211, 153, 0.4) !important;
        border-radius: 28px;
        padding: 3.5rem 3rem !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"]::before {
        content: '';
        position: absolute;
        top: -30%;
        left: -30%;
        width: 160%;
        height: 160%;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.04) 0%, transparent 70%);
        pointer-events: none;
    }
    
    div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 60px -12px rgba(52, 211, 153, 0.2);
    }

    /* Inner Elements Animations */
    .logo-row, .section-label, .ai-badge, .hero-title, .hero-sub, .waves, .fine-print {
        animation: fadeInUp 0.8s ease-out both;
    }
    
    .logo-row { animation-delay: 0.4s; }
    .section-label { animation-delay: 0.5s; }
    .hero-title { animation-delay: 0.6s; }
    .hero-sub { animation-delay: 0.7s; }
    .waves { animation-delay: 0.8s; }
    .fine-print { animation-delay: 0.9s; }

    /* Logo row with circular badge */
    .logo-row {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 2rem;
    }
    
    .logo-row .flag {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(52, 211, 153, 0.25), rgba(52, 211, 153, 0.05));
        border: 2px solid #34d399;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.2);
    }
    
    .logo-row .brand {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    .section-label {
        color: #6ee7b7;
        letter-spacing: 3px;
        font-size: 0.8rem;
        font-weight: 800;
        margin-bottom: 2rem;
        text-transform: uppercase;
        border-left: 3px solid #34d399;
        padding-left: 10px;
    }

    .hero-title {
        color: #ffffff;
        font-size: clamp(1.8rem, 5vw, 2.6rem);
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 1.5rem;
    }
    
    .hero-title .accent {
        color: #34d399;
        text-shadow: 0 0 20px rgba(52, 211, 153, 0.4);
    }

    .hero-sub {
        color: #a7b5ad;
        font-size: 1.1rem;
        line-height: 1.8;
        margin-bottom: 2.5rem;
    }

    /* Customizing Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #061109 !important;
        border-radius: 14px;
        padding: 6px;
        border: 1px solid rgba(52, 211, 153, 0.2) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px !important;
        color: #9ca3af;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: #34d399 !important;
        color: #04140b !important;
        box-shadow: 0 4px 12px rgba(52, 211, 153, 0.3);
    }

    /* Input fields styling */
    .stTextInput input {
        background: #061109 !important;
        color: #ffffff !important;
        border: 2px solid rgba(52, 211, 153, 0.2) !important;
        border-radius: 12px !important;
        height: 54px !important;
        font-size: 1.05rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #34d399 !important;
        box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.1) !important;
    }

    /* Button styling */
    .stButton button {
        background: #34d399 !important;
        color: #04140b !important;
        border-radius: 12px !important;
        height: 56px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    .stButton button:hover {
        transform: scale(1.02);
        background: #22c55e !important;
        box-shadow: 0 10px 20px rgba(52, 211, 153, 0.3) !important;
    }

    /* Fine print */
    .fine-print {
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 2rem;
        text-align: center;
    }
    
    .fine-print a { color: #34d399; text-decoration: none; font-weight: 600; }

    /* Mobile adjustments */
    @media (max-width: 1024px) {
        [data-testid="stHorizontalBlock"] { padding: 2rem 1rem !important; }
        div[data-testid="column"]:has(> div .login-marker),
        div[data-testid="column"]:has(> div .hero-marker) {
            flex: 0 1 100% !important;
            max-width: 500px !important;
        }
    }
</style>
"""

# Dashboard CSS with circular gauges and patterns
DASHBOARD_CSS = """
<style>
    /* Circular risk gauge styling */
    .risk-gauge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #0d1a13 0%, #061109 100%);
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .risk-gauge-container:hover {
        border-color: rgba(52, 211, 153, 0.4);
        box-shadow: 0 8px 24px rgba(52, 211, 153, 0.1);
    }

    .gauge-title {
        color: #a7b5ad;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .gauge-value {
        color: #34d399;
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
    }

    .gauge-label {
        color: #6b7280;
        font-size: 0.85rem;
    }

    /* Circular badge styling */
    .risk-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        border: 2px solid;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
    }

    .risk-badge.high {
        background: radial-gradient(circle at 30% 30%, rgba(239, 68, 68, 0.3), rgba(239, 68, 68, 0.05));
        border-color: #ef4444;
        color: #fca5a5;
    }

    .risk-badge.medium {
        background: radial-gradient(circle at 30% 30%, rgba(245, 158, 11, 0.3), rgba(245, 158, 11, 0.05));
        border-color: #f59e0b;
        color: #fcd34d;
    }

    .risk-badge.low {
        background: radial-gradient(circle at 30% 30%, rgba(34, 197, 94, 0.3), rgba(34, 197, 94, 0.05));
        border-color: #22c55e;
        color: #86efac;
    }

    /* Progress ring animation */
    .progress-ring {
        transform: rotate(-90deg);
        transform-origin: 50% 50%;
    }

    .progress-ring-circle {
        transition: stroke-dashoffset 0.5s ease;
        stroke-dasharray: 282.7;
    }

    /* Circular stat card */
    .stat-card-circular {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: linear-gradient(135deg, #0d1a13 0%, #061109 100%);
        border: 1px solid rgba(52, 211, 153, 0.15);
        border-radius: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .stat-card-circular:hover {
        border-color: rgba(52, 211, 153, 0.3);
        box-shadow: 0 8px 24px rgba(52, 211, 153, 0.1);
        transform: translateY(-4px);
    }

    .stat-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(52, 211, 153, 0.2), rgba(52, 211, 153, 0.02));
        border: 2px solid rgba(52, 211, 153, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        font-size: 2rem;
        font-weight: 900;
        color: #34d399;
    }

    .stat-label {
        color: #a7b5ad;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Decorative circular patterns */
    .circular-pattern-bg {
        position: relative;
        overflow: hidden;
    }

    .circular-pattern-bg::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.03) 0%, transparent 70%);
        pointer-events: none;
    }

    .circular-pattern-bg::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -30%;
        width: 160%;
        height: 160%;
        background: radial-gradient(circle, rgba(34, 197, 94, 0.02) 0%, transparent 70%);
        pointer-events: none;
    }

    /* Risk level indicator with circular design */
    .risk-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.5rem;
        box-shadow: 0 0 8px currentColor;
    }

    .risk-indicator.high {
        background-color: #ef4444;
        color: #ef4444;
    }

    .risk-indicator.medium {
        background-color: #f59e0b;
        color: #f59e0b;
    }

    .risk-indicator.low {
        background-color: #22c55e;
        color: #22c55e;
    }
</style>
"""


def create_circular_gauge_svg(value, max_value=100, label=""):
    """Create an SVG circular gauge/progress ring."""
    percentage = min(value / max_value, 1.0)
    circumference = 2 * math.pi * 45
    stroke_dashoffset = circumference * (1 - percentage)
    
    # Determine color based on value
    if value >= 60:
        color = "#ef4444"  # Red for high risk
    elif value >= 40:
        color = "#f59e0b"  # Orange for medium risk
    else:
        color = "#22c55e"  # Green for low risk
    
    svg = f"""
    <svg width="140" height="140" viewBox="0 0 140 140" style="margin: 0 auto; display: block;">
        <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:1" />
            </linearGradient>
        </defs>
        <!-- Background circle -->
        <circle cx="70" cy="70" r="60" fill="none" stroke="rgba(52, 211, 153, 0.1)" stroke-width="8"/>
        <!-- Progress circle -->
        <circle cx="70" cy="70" r="60" fill="none" stroke="url(#gaugeGradient)" stroke-width="8" 
                stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}"
                stroke-linecap="round" style="transform: rotate(-90deg); transform-origin: 70px 70px; transition: stroke-dashoffset 0.5s ease;"/>
        <!-- Center text -->
        <text x="70" y="75" text-anchor="middle" font-size="28" font-weight="900" fill="{color}">{int(value)}</text>
        <text x="70" y="95" text-anchor="middle" font-size="12" fill="#a7b5ad">{label}</text>
    </svg>
    """
    return svg


def create_risk_badge_svg(risk_level):
    """Create a circular badge for risk level."""
    if risk_level.lower() == "high":
        color = "#ef4444"
        bg_color = "rgba(239, 68, 68, 0.1)"
    elif risk_level.lower() == "medium":
        color = "#f59e0b"
        bg_color = "rgba(245, 158, 11, 0.1)"
    else:
        color = "#22c55e"
        bg_color = "rgba(34, 197, 94, 0.1)"
    
    svg = f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <defs>
            <radialGradient id="badgeGradient" cx="30%" cy="30%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.05" />
            </radialGradient>
        </defs>
        <circle cx="50" cy="50" r="45" fill="url(#badgeGradient)" stroke="{color}" stroke-width="2"/>
        <text x="50" y="60" text-anchor="middle" font-size="16" font-weight="700" fill="{color}" text-transform="uppercase">{risk_level[0]}</text>
    </svg>
    """
    return svg


def login_view():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    # Use columns to center the cards and give them a layout
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="login-marker"></div>
            <div class="logo-row">
                <span class="flag">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z" fill="#34d399"/>
                    </svg>
                </span>
                <span class="brand">Contract Analyzer</span>
            </div>
            <div class="section-label">Account Access</div>
            """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="login_pw",
                                      placeholder="••••••••")
            if st.button("Login Now", key="login_btn"):
                r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    me = requests.get(f"{API_URL}/auth/me", headers=auth_headers()).json()
                    st.session_state.user = me
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Login failed"))

        with tab2:
            name = st.text_input("Full Name", placeholder="John Doe")
            email_r = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            pw_r = st.text_input("Password", type="password", key="reg_pw",
                                  placeholder="Create a password")
            if st.button("Create Account", key="register_btn"):
                r = requests.post(f"{API_URL}/auth/register",
                                   json={"full_name": name, "email": email_r, "password": pw_r})
                if r.status_code == 201:
                    st.success("Registered! Please log in.")
                else:
                    st.error(r.json().get("detail", "Registration failed"))

        st.markdown(
            """
            <div class="fine-print">
                Secure access to your legal insights. <br>
                By continuing you agree to our <a href="#">Terms</a>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="hero-marker"></div>
            <div class="hero-title">
                Analyze Contracts with <span class="accent">AI Precision</span>
            </div>
            <div class="hero-sub">
                Upload any agreement and we'll automatically flag termination windows, 
                auto-renewals, and liability exposure in seconds.
            </div>
            <svg class="waves" width="100%" height="80" viewBox="0 0 420 80" preserveAspectRatio="xMidYMid meet" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 60 Q60 20 140 60 T280 60 T420 60" stroke="#34d399" stroke-width="2" opacity="0.8"/>
                <path d="M0 72 Q60 32 140 72 T280 72 T420 72" stroke="#34d399" stroke-width="1.5" opacity="0.4"/>
            </svg>
            """,
            unsafe_allow_html=True,
        )


def main_app():
    st.sidebar.title(f"👋 {st.session_state.user['full_name']}")
    st.sidebar.caption(f"Role: {st.session_state.user['role']}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Dashboard", "Upload & Analyze", "My Documents", "Search"])

    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload & Analyze":
        show_upload()
    elif page == "My Documents":
        show_documents()
    elif page == "Search":
        show_search()


def show_dashboard():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.header("📊 AI Insights Dashboard")
    
    r = requests.get(f"{API_URL}/dashboard", headers=auth_headers())
    if r.status_code != 200:
        st.error("Failed to load dashboard")
        return
    
    stats = r.json()
    
    # Create circular gauge displays
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card-circular">', unsafe_allow_html=True)
        st.markdown('<div class="stat-circle">📄</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #34d399; font-size: 1.8rem; font-weight: 900;">{stats.get("total_documents", 0)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Documents</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        high_risk = stats.get("high_risk_documents", 0)
        st.markdown('<div class="stat-card-circular">', unsafe_allow_html=True)
        st.markdown(create_circular_gauge_svg(high_risk * 10, 100, "High Risk"), unsafe_allow_html=True)
        st.markdown('<div class="stat-label">High Risk Count</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        avg_risk = stats.get("average_risk_score", 0)
        st.markdown('<div class="stat-card-circular">', unsafe_allow_html=True)
        st.markdown(create_circular_gauge_svg(avg_risk, 100, "Avg Risk"), unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Average Risk Score</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card-circular">', unsafe_allow_html=True)
        st.markdown('<div class="stat-circle">⚡</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #34d399; font-size: 1.8rem; font-weight: 900;">{len(stats.get("frequently_detected_risks", []))}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Risk Types</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # Risk distribution with circular badges
    st.subheader("🎯 Frequently Detected Risks")
    frequent = stats.get("frequently_detected_risks", [])
    
    if frequent:
        risk_cols = st.columns(min(5, len(frequent)))
        for idx, risk in enumerate(frequent[:5]):
            with risk_cols[idx]:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #0d1a13 0%, #061109 100%); 
                    border: 1px solid rgba(52, 211, 153, 0.15); border-radius: 16px;">
                        <div style="width: 60px; height: 60px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, rgba(52, 211, 153, 0.2), rgba(52, 211, 153, 0.02)); 
                        border: 2px solid rgba(52, 211, 153, 0.3); display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem; font-size: 1.5rem; font-weight: 900; color: #34d399;">
                            {risk['count']}
                        </div>
                        <div style="color: #a7b5ad; font-size: 0.85rem; font-weight: 600; word-wrap: break-word;">{risk['title'][:20]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No risks detected yet.")

    st.divider()
    st.subheader("📋 Recent Analyses")
    recent = stats.get("recent_documents", [])
    if recent:
        for doc in recent:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 **{doc['filename']}**")
                st.caption(doc.get("summary", "No summary available")[:100] + "...")
            with col2:
                risk_level = doc['risk_level'].lower()
                if risk_level == "high":
                    st.markdown('<span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #ef4444; box-shadow: 0 0 8px #ef4444; margin-right: 0.5rem;"></span><span style="color: #ef4444; font-weight: 700;">HIGH</span>', unsafe_allow_html=True)
                elif risk_level == "medium":
                    st.markdown('<span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #f59e0b; box-shadow: 0 0 8px #f59e0b; margin-right: 0.5rem;"></span><span style="color: #f59e0b; font-weight: 700;">MEDIUM</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #22c55e; box-shadow: 0 0 8px #22c55e; margin-right: 0.5rem;"></span><span style="color: #22c55e; font-weight: 700;">LOW</span>', unsafe_allow_html=True)
    else:
        st.info("No documents analyzed yet.")


def show_upload():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.header("📤 Upload & Analyze Document")
    uploaded_file = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])
    if uploaded_file:
        with st.spinner("Analyzing document..."):
            files = {"file": uploaded_file}
            r = requests.post(f"{API_URL}/documents/upload", headers=auth_headers(), files=files)
            if r.status_code == 200:
                result = r.json()
                st.success("Document analyzed successfully!")
                st.json(result)
            else:
                st.error("Failed to analyze document")


def show_documents():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.header("📚 My Documents")
    r = requests.get(f"{API_URL}/documents", headers=auth_headers())
    if r.status_code == 200:
        docs = r.json()
        if docs:
            for doc in docs:
                with st.expander(f"📄 {doc['filename']} - {doc['risk_level']}"):
                    st.write(f"Uploaded: {doc.get('uploaded_at', 'N/A')}")
                    st.write(f"Summary: {doc.get('summary', 'N/A')}")
        else:
            st.info("No documents found.")
    else:
        st.error("Failed to load documents")


def show_search():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.header("🔍 Search Documents")
    query = st.text_input("Enter search query")
    if query:
        with st.spinner("Searching..."):
            r = requests.get(f"{API_URL}/search", headers=auth_headers(), params={"query": query})
            if r.status_code == 200:
                results = r.json()
                st.write(f"Found {len(results)} results")
                for result in results:
                    st.write(result)
            else:
                st.error("Search failed")


if __name__ == "__main__":
    if st.session_state.token:
        main_app()
    else:
        login_view()
