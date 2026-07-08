import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000") if hasattr(st, "secrets") else "http://localhost:8000"
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = "http://localhost:8000"

st.set_page_config(page_title="Contract Risk Analyzer", page_icon="⚖️", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None


# ────────────────────────────────────────────────────────────────────────────
# THEME
# ────────────────────────────────────────────────────────────────────────────
def inject_theme():
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
        :root{
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

        html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

        .stApp{
            background: var(--bg);
            color: var(--text);
        }

        #MainMenu, footer, header[data-testid="stHeader"] { background: transparent; }
        header[data-testid="stHeader"] { background: var(--bg); }

        .block-container{
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 { color: #ffffff !important; font-weight: 800 !important; }
        p, span, label, .stMarkdown, .stCaption { color: var(--text-soft); }

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"]{
            background: linear-gradient(180deg, #08201548 0%, #05170f 100%), var(--bg-2);
            border-right: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3{
            color: #fff !important;
        }
        section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] p{
            color: var(--text-soft) !important;
        }

        /* Sidebar radio nav styled like a menu */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div{
            gap: 4px;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label{
            padding: 10px 14px !important;
            border-radius: 10px;
            border: 1px solid transparent;
            transition: all .15s ease;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover{
            background: rgba(255,255,255,0.04);
            border-color: var(--line);
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child{
            border-color: var(--green-3) !important;
        }

        /* ===== Text inputs / text areas / selects ===== */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-baseweb="select"] > div,
        div[data-testid="stNumberInput"] input{
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid var(--line) !important;
            border-radius: 10px !important;
            color: #fff !important;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus{
            border-color: var(--green-3) !important;
            background: rgba(52,217,128,0.06) !important;
        }
        div[data-testid="stTextInput"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stFileUploader"] label{
            color: var(--text-soft) !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }

        /* ===== Buttons ===== */
        .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button{
            width: 100%;
            background: linear-gradient(180deg, var(--green-3), var(--green-2));
            color: #04170e !important;
            font-weight: 700 !important;
            border: none;
            border-radius: 10px;
            padding: 0.65rem 0;
            box-shadow: 0 10px 24px -8px rgba(34,199,110,0.55);
            transition: filter .15s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover{
            filter: brightness(1.08);
            color: #04170e !important;
        }
        .stButton > button:active{
            filter: brightness(0.95);
        }

        /* ===== Tabs ===== */
        div[data-testid="stTabs"] div[role="tablist"]{
            gap: 4px;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 4px;
        }
        div[data-testid="stTabs"] button[role="tab"]{
            border-radius: 9px;
            color: var(--text-soft);
            font-weight: 600;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{
            background: linear-gradient(180deg, var(--green-3), var(--green-2));
            color: #04170e !important;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p{
            color: #04170e !important;
        }

        /* ===== Metrics ===== */
        div[data-testid="stMetric"]{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 16px 18px;
        }
        div[data-testid="stMetricLabel"] { color: var(--text-soft) !important; }
        div[data-testid="stMetricValue"] { color: var(--green-3) !important; }

        /* ===== Expander ===== */
        div[data-testid="stExpander"]{
            background: var(--panel);
            border: 1px solid var(--line) !important;
            border-radius: 12px;
        }

        /* ===== File uploader ===== */
        div[data-testid="stFileUploaderDropzone"]{
            background: rgba(255,255,255,0.04);
            border: 1px dashed var(--line) !important;
            border-radius: 12px;
        }

        /* ===== Tables ===== */
        div[data-testid="stTable"], .stDataFrame{
            background: var(--panel);
            border-radius: 12px;
        }

        /* ===== Alerts ===== */
        div[data-testid="stAlert"]{
            border-radius: 10px;
            border: 1px solid var(--line);
        }

        hr{ border-color: var(--line) !important; }

        /* ===== Auth screen specific ===== */
        .auth-shell{
            display:flex;
            min-height: 100vh;
            margin: -2rem -1rem -3rem -1rem;
        }
        .auth-logo{
            display:flex; align-items:center; gap:10px;
            font-size: 20px; font-weight:800; color:#fff;
            margin-bottom: 30px;
        }
        .auth-heading{
            font-size: 13px;
            font-weight:600;
            color: var(--text-soft);
            text-transform:uppercase;
            letter-spacing: 0.06em;
            margin: 0 0 8px;
        }
        .auth-foot{
            font-size: 12.5px;
            color: var(--text-soft);
            opacity:0.65;
            line-height:1.6;
            margin-top: 20px;
        }
        .auth-foot a{ color: var(--green-3); text-decoration:none; }

        .hero-panel{
            position:relative;
            border-radius: 20px;
            overflow:hidden;
            display:flex;
            align-items:center;
            justify-content:center;
            padding: 60px 40px;
            min-height: 520px;
            background: linear-gradient(180deg, #04140d 0%, #061a11 100%);
            border: 1px solid var(--line);
        }
        .orb{ position:absolute; border-radius:50%; pointer-events:none; }
        .orb-1{ width: 480px; height:480px; right: -160px; top: -160px;
            background: radial-gradient(circle at 35% 30%, rgba(52,217,128,0.55), rgba(15,107,69,0.15) 60%, transparent 75%); }
        .orb-2{ width: 320px; height:320px; right: -20px; top: 30px;
            border: 1px solid rgba(52,217,128,0.35);
            background: radial-gradient(circle at 30% 25%, rgba(23,167,95,0.55), transparent 70%); }
        .orb-3{ width: 200px; height:200px; right: 160px; top: 160px;
            border: 1px solid rgba(52,217,128,0.28); }
        .orb-4{ width: 110px; height:110px; left: 40px; bottom: 60px;
            border: 1px solid rgba(52,217,128,0.22);
            background: radial-gradient(circle at 35% 30%, rgba(23,167,95,0.25), transparent 70%); }

        .hero-copy{ position:relative; z-index:2; max-width: 520px; text-align:center; }
        .eyebrow{
            display:inline-flex; align-items:center; gap:8px;
            font-size: 13px; font-weight:600; color: var(--green-3);
            text-transform:uppercase; letter-spacing:0.08em;
            background: rgba(52,217,128,0.08);
            border: 1px solid rgba(52,217,128,0.25);
            padding: 7px 14px; border-radius: 999px; margin-bottom: 22px;
        }
        .eyebrow::before{
            content:''; width:6px; height:6px; border-radius:50%;
            background: var(--green-3); box-shadow: 0 0 8px var(--green-glow);
            display:inline-block;
        }
        .hero-copy h1{
            font-size: clamp(24px, 2.6vw, 34px);
            font-weight:800; line-height:1.2; letter-spacing:-0.01em;
            margin: 0 0 18px; color:#fff;
        }
        .hero-copy h1 span{
            background: linear-gradient(180deg, var(--green-3), var(--green-2));
            -webkit-background-clip: text; background-clip: text; color: transparent;
        }
        .hero-copy p{
            font-size:15px; line-height:1.7; color: var(--text-soft);
            max-width: 460px; margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


LOGO_SVG = """
<div class="auth-logo">
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="26" height="26">
    <path d="M4 3v18l8-5 8 5V3a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1z" fill="url(#g)"/>
    <defs>
      <linearGradient id="g" x1="4" y1="2" x2="20" y2="21" gradientUnits="userSpaceOnUse">
        <stop stop-color="#34d980"/>
        <stop offset="1" stop-color="#0f6b45"/>
      </linearGradient>
    </defs>
  </svg>
  Contract Analyzer
</div>
"""

HERO_HTML = """
<div class="hero-panel">
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>
  <div class="orb orb-4"></div>
  <div class="hero-copy">
    <div class="eyebrow">AI-Powered</div>
    <h1>Welcome to the <span>Contract &amp; Legal<br>Document Risk Analyzer</span></h1>
    <p>Please login or register to continue. Once you're in, upload any agreement and we'll flag
    termination windows, auto-renewals, and liability exposure in seconds.</p>
  </div>
</div>
"""


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def login_view():
    left, right = st.columns([1, 1.3], gap="large")

    with left:
        st.markdown(LOGO_SVG, unsafe_allow_html=True)
        st.markdown('<p class="auth-heading">Login / Register</p>', unsafe_allow_html=True)

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
            name = st.text_input("Full Name", key="reg_name", placeholder="Enter your full name")
            email_r = st.text_input("Email", key="reg_email", placeholder="Enter your email")
            pw_r = st.text_input("Password", type="password", key="reg_pw",
                                  placeholder="Choose a password")
            if st.button("Create account", key="reg_btn"):
                r = requests.post(f"{API_URL}/auth/register",
                                   json={"full_name": name, "email": email_r, "password": pw_r})
                if r.status_code == 201:
                    st.success("Registered! Please log in.")
                else:
                    st.error(r.json().get("detail", "Registration failed"))

        st.markdown(
            '<div class="auth-foot">By continuing you agree to our '
            '<a href="#">Terms</a> and <a href="#">Privacy Policy</a>.</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(HERO_HTML, unsafe_allow_html=True)


def main_app():
    st.sidebar.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.sidebar.markdown(f"### 👋 {st.session_state.user['full_name']}")
    st.sidebar.caption(f"Role: {st.session_state.user['role']}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate", ["Dashboard", "Upload & Analyze", "My Documents", "Search"],
                             label_visibility="collapsed")

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
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Documents", stats["total_documents"])
    c2.metric("Average Risk Score", stats["average_risk_score"])
    c3.metric("High-Risk Documents", stats["high_risk_documents"])

    st.subheader("Frequently Detected Risks")
    if stats["frequently_detected_risks"]:
        st.table(stats["frequently_detected_risks"])
    else:
        st.info("No risk data yet — analyze a document first.")


def show_upload():
    st.header("📤 Upload & Analyze a Document")
    file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
    if file and st.button("Upload"):
        files = {"file": (file.name, file.getvalue())}
        r = requests.post(f"{API_URL}/documents/upload", headers=auth_headers(), files=files)
        if r.status_code == 201:
            doc = r.json()
            st.success(f"Uploaded: {doc['filename']} (ID: {doc['id']})")
            with st.spinner("Running AI analysis..."):
                ar = requests.post(f"{API_URL}/documents/{doc['id']}/analyze", headers=auth_headers())
            if ar.status_code == 200:
                render_analysis(ar.json())
            else:
                st.error(ar.json().get("detail", "Analysis failed"))
        else:
            st.error(r.json().get("detail", "Upload failed"))


def show_documents():
    st.header("📁 My Documents")
    r = requests.get(f"{API_URL}/documents", headers=auth_headers())
    docs = r.json() if r.status_code == 200 else []
    if not docs:
        st.info("No documents yet.")
        return

    for doc in docs:
        with st.expander(f"{doc['filename']} — {doc['status']}"):
            col1, col2, col3 = st.columns(3)
            if col1.button("View Analysis", key=f"view_{doc['id']}"):
                ar = requests.get(f"{API_URL}/documents/{doc['id']}/analysis", headers=auth_headers())
                if ar.status_code == 200:
                    render_analysis(ar.json())
                else:
                    st.warning("Not analyzed yet. Re-upload or trigger analysis.")
            if col2.button("Download PDF Report", key=f"pdf_{doc['id']}"):
                pr = requests.get(f"{API_URL}/reports/{doc['id']}/pdf", headers=auth_headers())
                if pr.status_code == 200:
                    st.download_button("Save PDF", pr.content, file_name=f"{doc['filename']}_report.pdf",
                                        key=f"dlpdf_{doc['id']}")
            if col3.button("Delete", key=f"del_{doc['id']}"):
                requests.delete(f"{API_URL}/documents/{doc['id']}", headers=auth_headers())
                st.rerun()


def show_search():
    st.header("🔍 Semantic Search")
    r = requests.get(f"{API_URL}/documents", headers=auth_headers())
    docs = r.json() if r.status_code == 200 else []
    analyzed = [d for d in docs if d["status"] == "analyzed"]
    if not analyzed:
        st.info("Analyze a document first to enable search.")
        return

    doc_map = {f"{d['filename']} (ID {d['id']})": d["id"] for d in analyzed}
    choice = st.selectbox("Select document", list(doc_map.keys()))
    query = st.text_input("Ask a question, e.g. 'Show payment terms'")
    if st.button("Search") and query:
        payload = {"document_id": doc_map[choice], "query": query, "top_k": 5}
        r = requests.post(f"{API_URL}/search", headers=auth_headers(), json=payload)
        if r.status_code == 200:
            results = r.json()
            for res in results:
                st.markdown(f"**Relevance: {round(res['score']*100)}%**")
                st.write(res["text"])
                st.divider()
        else:
            st.error(r.json().get("detail", "Search failed"))


def render_analysis(a: dict):
    st.subheader("📄 AI Analysis Results")
    st.metric("Risk Score", f"{a['risk_score']} / 100")
    st.caption(f"Engine used: {a['engine_used']}")

    st.write("**Contract Type:**", a.get("contract_type"))
    st.write("**Parties:**", ", ".join(a.get("parties") or []))
    st.write("**Effective Date:**", a.get("effective_date"))
    st.write("**Expiry Date:**", a.get("expiry_date"))

    st.markdown("### Executive Summary")
    st.write(a.get("executive_summary"))

    st.markdown("### Risk Findings")
    for risk in a.get("risks", []):
        color = {"high": "🔴", "medium": "🟠", "low": "🟡"}.get(risk["severity"], "⚪")
        st.markdown(f"{color} **[{risk['severity'].upper()}] {risk['title']}** "
                     f"— confidence {round(risk['confidence']*100)}%")
        st.write(risk["explanation"])

    st.markdown("### Recommended Actions")
    for action in a.get("recommended_actions") or []:
        st.write(f"- {action}")


inject_theme()

if st.session_state.token is None:
    login_view()
else:
    main_app()
