import streamlit as st
import requests

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


LOGIN_CSS = """
<style>
    * {box-sizing: border-box;}
    html, body {margin: 0; padding: 0;}
    
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    .stApp {background: linear-gradient(135deg, #061109 0%, #0a1f14 100%); margin: 0; padding: 0;}

    /* Animations */
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-60px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(60px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
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
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    /* Main container */
    [data-testid="stHorizontalBlock"] {
        gap: 2rem !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100vh;
        margin: 0 !important;
        padding: 2rem !important;
        flex-wrap: wrap;
    }
    
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        display: flex !important;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* Left card - Credentials */
    div[data-testid="column"]:has(> div .login-marker) {
        flex: 0 1 420px !important;
        max-width: 420px !important;
        animation: slideInLeft 0.9s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"] {
        width: 100% !important;
        background: rgba(13, 26, 19, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(52, 211, 153, 0.25);
        border-radius: 24px;
        padding: 3rem 2.5rem !important;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.4),
            0 0 1px rgba(52, 211, 153, 0.5),
            inset 0 1px 0 rgba(52, 211, 153, 0.2);
        animation: fadeInUp 0.9s cubic-bezier(0.34, 1.56, 0.64, 1) 0.15s both, float 6s ease-in-out 2s infinite;
    }

    /* Right card - Welcome */
    div[data-testid="column"]:has(> div .hero-marker) {
        flex: 0 1 420px !important;
        max-width: 420px !important;
        animation: slideInRight 0.9s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"] {
        width: 100% !important;
        background: rgba(4, 20, 11, 0.5);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: 24px;
        padding: 3rem 2.5rem !important;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.3),
            0 0 1px rgba(52, 211, 153, 0.3),
            inset 0 1px 0 rgba(52, 211, 153, 0.15);
        animation: fadeInUp 0.9s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s both, float 6s ease-in-out 2.5s infinite;
    }

    /* Logo row */
    .logo-row {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 2rem;
        flex-wrap: nowrap;
        animation: fadeInUp 0.9s ease-out 0.4s both;
    }
    
    .logo-row .flag {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: rgba(52, 211, 153, 0.15);
        flex-shrink: 0;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    
    .logo-row .brand {
        color: #f5f7f6;
        font-size: 1.3rem;
        font-weight: 700;
        white-space: nowrap;
    }

    .section-label {
        color: #6ee7b7;
        letter-spacing: 2px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        animation: fadeInUp 0.9s ease-out 0.45s both;
    }

    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(52, 211, 153, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.4);
        color: #4ade80;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        margin-bottom: 1.5rem;
        letter-spacing: 1px;
        width: fit-content;
        animation: fadeInUp 0.9s ease-out 0.5s both;
    }
    
    .ai-badge .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #4ade80;
        flex-shrink: 0;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .hero-title {
        color: #f5f7f6;
        font-size: clamp(1.5rem, 4vw, 2.4rem);
        font-weight: 800;
        line-height: 1.3;
        margin-bottom: 1.2rem;
        max-width: 100%;
        word-wrap: break-word;
        animation: fadeInUp 0.9s ease-out 0.5s both;
    }
    
    .hero-title .accent {
        color: #4ade80;
        background: linear-gradient(135deg, #4ade80, #22c55e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-sub {
        color: #b9c4bd;
        font-size: clamp(0.95rem, 2vw, 1.05rem);
        line-height: 1.7;
        max-width: 100%;
        margin-bottom: 2rem;
        animation: fadeInUp 0.9s ease-out 0.6s both;
    }

    .waves {
        margin-top: 1.5rem;
        opacity: 0.6;
        max-width: 100%;
        height: auto;
        animation: fadeInUp 0.9s ease-out 0.7s both;
    }

    /* Tabs - Responsive */
    .stTabs {
        margin-bottom: 1.5rem;
        width: 100%;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(13, 26, 19, 0.4) !important;
        border-radius: 12px;
        padding: 6px;
        gap: 8px !important;
        width: 100% !important;
        display: flex !important;
        border-bottom: none !important;
        flex-wrap: wrap !important;
        border: 1px solid rgba(52, 211, 153, 0.15) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px !important;
        color: #9ca3af;
        font-weight: 600;
        padding: 12px 16px !important;
        flex: 1 1 0 !important;
        justify-content: center;
        display: flex !important;
        align-items: center;
        margin: 0 !important;
        min-height: 44px;
        font-size: 1rem;
        white-space: nowrap;
        border: 1px solid transparent !important;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #34d399, #22c55e) !important;
        color: #04140b !important;
        box-shadow: 0 4px 15px rgba(52, 211, 153, 0.3);
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }
    
    .stTabs [data-testid="stMarkdownContainer"] p {
        font-weight: inherit;
        margin: 0;
    }

    /* Input fields - Responsive */
    .stTextInput {
        width: 100%;
        margin-bottom: 1.2rem;
    }
    
    .stTextInput > label {
        color: #d1d5db !important;
        font-weight: 600;
        font-size: 0.9rem;
        display: block;
        margin-bottom: 0.6rem;
    }
    
    .stTextInput input {
        background: rgba(13, 26, 19, 0.5) !important;
        color: #f5f7f6 !important;
        border: 1px solid rgba(52, 211, 153, 0.2) !important;
        border-radius: 10px !important;
        padding: 0.85rem 1.1rem !important;
        width: 100% !important;
        font-size: 1rem;
        min-height: 48px;
        box-sizing: border-box;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border: 1px solid #34d399 !important;
        box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.1) !important;
        background: rgba(13, 26, 19, 0.7) !important;
    }
    
    .stTextInput input::placeholder {
        color: #5b6660;
    }

    /* Buttons - Responsive */
    div[data-testid="stButton"] {
        width: 100%;
        margin-bottom: 0.75rem;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #34d399, #22c55e);
        color: #04140b;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 1rem !important;
        width: 100% !important;
        min-height: 48px;
        transition: all 0.3s ease;
        font-size: 1.1rem;
        cursor: pointer;
        box-sizing: border-box;
        display: block !important;
        box-shadow: 0 4px 15px rgba(52, 211, 153, 0.2);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(52, 211, 153, 0.3);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    .stButton button p {
        color: #04140b !important;
        font-weight: 700;
        margin: 0;
    }

    /* Fine print */
    .fine-print {
        color: #7c8a83;
        font-size: 0.8rem;
        margin-top: 1.5rem;
        line-height: 1.6;
        word-wrap: break-word;
        text-align: center;
        animation: fadeInUp 0.9s ease-out 0.8s both;
    }
    
    .fine-print a {
        color: #4ade80;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    .fine-print a:hover {
        color: #22c55e;
        text-decoration: underline;
    }

    /* Mobile responsiveness */
    @media (max-width: 1024px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column;
            height: auto;
            gap: 2rem;
        }
        
        div[data-testid="column"]:has(> div .login-marker),
        div[data-testid="column"]:has(> div .hero-marker) {
            flex: 0 1 100% !important;
            max-width: 100% !important;
        }
    }

    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            padding: 1.5rem 1rem !important;
        }
        
        div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"],
        div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"] {
            padding: 2rem 1.5rem !important;
        }
        
        .logo-row .brand {
            font-size: 1.1rem;
        }
        
        .hero-title {
            font-size: clamp(1.3rem, 3vw, 2rem);
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 8px !important;
            font-size: 0.9rem;
        }
    }

    @media (max-width: 480px) {
        [data-testid="stHorizontalBlock"] {
            padding: 1rem 0.75rem !important;
            gap: 1.5rem;
        }
        
        div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"],
        div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"] {
            padding: 1.5rem 1.2rem !important;
        }
        
        .logo-row {
            margin-bottom: 1.5rem;
        }
        
        .logo-row .brand {
            font-size: 1rem;
        }
        
        .hero-title {
            font-size: clamp(1.1rem, 2.5vw, 1.6rem);
            margin-bottom: 1rem;
        }
        
        .hero-sub {
            font-size: 0.9rem;
        }
        
        .stTextInput input {
            padding: 0.75rem 0.9rem !important;
        }
        
        .stButton button {
            padding: 0.85rem 0.8rem !important;
            font-size: 1rem;
        }
    }
</style>
"""


def login_view():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="login-marker"></div>
            <div class="logo-row">
                <span class="flag">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z" fill="#34d399"/>
                    </svg>
                </span>
                <span class="brand">Contract Analyzer</span>
            </div>
            <div class="section-label">Login / Register</div>
            """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", key="login_pw",
                                      placeholder="Enter your password")
            if st.button("Login", key="login_btn"):
                r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    me = requests.get(f"{API_URL}/auth/me", headers=auth_headers()).json()
                    st.session_state.user = me
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Login failed"))

        with tab2:
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email_r = st.text_input("Email", key="reg_email", placeholder="Enter your email")
            pw_r = st.text_input("Password", type="password", key="reg_pw",
                                  placeholder="Choose a password")
            if st.button("Register", key="register_btn"):
                r = requests.post(f"{API_URL}/auth/register",
                                   json={"full_name": name, "email": email_r, "password": pw_r})
                if r.status_code == 201:
                    st.success("Registered! Please log in.")
                else:
                    st.error(r.json().get("detail", "Registration failed"))

        st.markdown(
            """
            <div class="fine-print">
                By continuing you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="hero-marker"></div>
            <div class="hero-title">
                Welcome to the <span class="accent">Contract & Legal Document Risk Analyzer</span>
            </div>
            <div class="hero-sub">
                Please login or register to continue. Once you're in, upload any agreement
                and we'll flag termination windows, auto-renewals, and liability exposure in seconds.
            </div>
            <svg class="waves" width="100%" height="80" viewBox="0 0 420 80" preserveAspectRatio="xMidYMid meet" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 60 Q60 20 140 60 T280 60 T420 60" stroke="#2f5c40" stroke-width="1.5" opacity="0.7"/>
                <path d="M0 72 Q60 32 140 72 T280 72 T420 72" stroke="#2f5c40" stroke-width="1.5" opacity="0.5"/>
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
    st.header("📊 AI Insights Dashboard")
    r = requests.get(f"{API_URL}/dashboard", headers=auth_headers())
    if r.status_code != 200:
        st.error("Failed to load dashboard")
        return
    stats = r.json()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Documents", stats.get("total_documents", 0))
    with c2:
        st.metric("High Risk", stats.get("high_risk_count", 0))
    with c3:
        st.metric("Medium Risk", stats.get("medium_risk_count", 0))
    with c4:
        st.metric("Low Risk", stats.get("low_risk_count", 0))

    st.subheader("Recent Analyses")
    recent = stats.get("recent_documents", [])
    if recent:
        for doc in recent:
            with st.expander(f"📄 {doc['filename']} - Risk: {doc['risk_level']}"):
                st.write(doc.get("summary", "No summary available"))
    else:
        st.info("No documents analyzed yet.")


def show_upload():
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
    st.header("📚 My Documents")
    r = requests.get(f"{API_URL}/documents", headers=auth_headers())
    if r.status_code == 200:
        docs = r.json()
        if docs:
            for doc in docs:
                with st.expander(f"📄 {doc['filename']} - {doc['risk_level']}"):
                    st.write(f"Uploaded: {doc['created_at']}")
                    st.write(f"Summary: {doc.get('summary', 'N/A')}")
        else:
            st.info("No documents found.")
    else:
        st.error("Failed to load documents")


def show_search():
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
