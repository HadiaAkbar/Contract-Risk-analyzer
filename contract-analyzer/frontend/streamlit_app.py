import streamlit as st
import requests

# --- Configuration ---
# Default to localhost if not specified in secrets or environment
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Contract Risk Analyzer", layout="wide", initial_sidebar_state="expanded")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None

# --- API Helper ---
def call_api(method, endpoint, **kwargs):
    """Centralized API caller to handle headers and error reporting."""
    url = f"{API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = kwargs.pop("headers", {})
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        if response.status_code in [200, 201]:
            return response.json()
        
        # Handle errors gracefully
        try:
            detail = response.json().get("detail", "Unknown error")
        except:
            detail = f"Server Error ({response.status_code})"
        st.error(detail)
    except Exception as e:
        st.error(f"Connection failed: {e}")
    return None

# --- UI Components ---
def login_view():
    st.title("🔐 Contract Risk Analyzer")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            data = call_api("POST", "/auth/login", json={"email": email, "password": password})
            if data:
                st.session_state.token = data["access_token"]
                user = call_api("GET", "/auth/me")
                if user:
                    st.session_state.user = user
                    st.rerun()

    with tab2:
        name = st.text_input("Full Name")
        email_r = st.text_input("Email", key="reg_email")
        pw_r = st.text_input("Password", type="password", key="reg_pw")
        if st.button("Create Account"):
            if call_api("POST", "/auth/register", json={"full_name": name, "email": email_r, "password": pw_r}):
                st.success("Registered! Please log in.")

def main_app():
    st.sidebar.title(f"👋 {st.session_state.user['full_name']}")
    st.sidebar.caption(f"Role: {st.session_state.user['role'].upper()}")
    
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Dashboard", "Upload", "My Documents"])

    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload":
        show_upload()
    elif page == "My Documents":
        show_documents()

def show_dashboard():
    st.header("📊 Dashboard")
    stats = call_api("GET", "/dashboard")
    if stats:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Documents", stats.get("total_documents", 0))
        col2.metric("High Risk", stats.get("high_risk_documents", 0))
        col3.metric("Avg Risk Score", f"{stats.get('average_risk_score', 0):.1f}")

def show_upload():
    st.header("📤 Upload & Analyze")
    file = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])
    if file and st.button("Analyze"):
        with st.spinner("Processing..."):
            doc = call_api("POST", "/documents/upload", files={"file": file})
            if doc:
                result = call_api("POST", f"/documents/{doc['id']}/analyze")
                if result:
                    st.success("Analysis Complete!")
                    st.json(result)

def show_documents():
    st.header("📚 My Documents")
    docs = call_api("GET", "/documents")
    if docs:
        for doc in docs:
            with st.expander(f"📄 {doc['filename']}"):
                st.write(f"Status: {doc['status']}")
                if st.button("View Analysis", key=doc['id']):
                    analysis = call_api("GET", f"/documents/{doc['id']}/analysis")
                    if analysis:
                        st.json(analysis)

if __name__ == "__main__":
    if st.session_state.token:
        main_app()
    else:
        login_view()
