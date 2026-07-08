import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000") if hasattr(st, "secrets") else "http://localhost:8000"
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = "http://localhost:8000"

st.set_page_config(page_title="Contract Risk Analyzer", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def login_view():
    st.title("⚖️ AI Contract & Legal Document Risk Analyzer")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
            if r.status_code == 200:
                st.session_state.token = r.json()["access_token"]
                me = requests.get(f"{API_URL}/auth/me", headers=auth_headers()).json()
                st.session_state.user = me
                st.rerun()
            else:
                st.error(r.json().get("detail", "Login failed"))

    with tab2:
        name = st.text_input("Full Name")
        email_r = st.text_input("Email", key="reg_email")
        pw_r = st.text_input("Password", type="password", key="reg_pw")
        if st.button("Register"):
            r = requests.post(f"{API_URL}/auth/register",
                               json={"full_name": name, "email": email_r, "password": pw_r})
            if r.status_code == 201:
                st.success("Registered! Please log in.")
            else:
                st.error(r.json().get("detail", "Registration failed"))


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


if st.session_state.token is None:
    login_view()
else:
    main_app()
