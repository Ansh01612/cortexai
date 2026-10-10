import os
from urllib.parse import urlparse

import requests
import streamlit as st

st.set_page_config(
    page_title="CortexAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; max-width: 1200px;}
      .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #172554, #4c1d95);
        color: white;
        margin-bottom: 1.2rem;
      }
      .hero h1 {margin: 0 0 .4rem 0;}
      .hero p {margin: 0; opacity: .9;}
    </style>
    """,
    unsafe_allow_html=True,
)

frontend_url = os.getenv("CORTEX_FRONTEND_URL", "").strip().rstrip("/")
api_url = os.getenv("CORTEX_API_URL", "").strip().rstrip("/")

with st.sidebar:
    st.title("🧠 CortexAI")
    st.caption("AI workspace")
    st.markdown("---")
    st.markdown("**Configuration**")
    st.write("Frontend URL:", frontend_url or "Not configured")
    st.write("API URL:", api_url or "Not configured")
    st.info(
        "Set CORTEX_FRONTEND_URL and CORTEX_API_URL in your deployment's "
        "environment/secrets to connect your existing CortexAI services."
    )

st.markdown(
    """
    <div class="hero">
      <h1>🧠 CortexAI</h1>
      <p>Your AI workspace — launch the existing app and check service connectivity.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

overview, launch, health = st.tabs(["Overview", "Open CortexAI", "Service health"])

with overview:
    st.subheader("Welcome")
    st.write(
        "This Streamlit interface is a lightweight companion for the existing "
        "CortexAI React + Node.js application. It does not replace the original "
        "frontend, authentication, database, or backend microservices."
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Frontend", "React / Vite")
    col2.metric("Backend", "Node.js")
    col3.metric("Data services", "MongoDB + Redis")
    st.markdown("### Get started")
    st.markdown(
        "1. Deploy your existing CortexAI frontend and backend.\n"
        "2. Add their public URLs as environment variables.\n"
        "3. Use **Open CortexAI** to launch the app or **Service health** to test the API."
    )

with launch:
    st.subheader("Open the existing CortexAI app")
    if frontend_url:
        parsed = urlparse(frontend_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            st.error("CORTEX_FRONTEND_URL must be a valid http:// or https:// URL.")
        else:
            st.link_button("Launch CortexAI ↗", frontend_url, use_container_width=True)
            st.caption(f"Configured frontend: {frontend_url}")
            show_embed = st.checkbox("Try displaying the app inside this page", value=False)
            if show_embed:
                st.warning(
                    "Some sites block embedding with browser security headers. "
                    "If the embedded view is blank, use the Launch button instead."
                )
                st.components.v1.iframe(frontend_url, height=760, scrolling=True)
    else:
        st.warning("No frontend URL configured yet.")
        st.code(
            "CORTEX_FRONTEND_URL=https://your-cortexai-frontend.example.com",
            language="bash",
        )

with health:
    st.subheader("API health check")
    if not api_url:
        st.warning("Set CORTEX_API_URL to your deployed gateway/API base URL.")
        st.code("CORTEX_API_URL=https://your-cortexai-api.example.com", language="bash")
    else:
        health_url = f"{api_url}/api/health"
        st.write(f"Checking: `{health_url}`")
        if st.button("Check API health", type="primary"):
            try:
                response = requests.get(health_url, timeout=10)
                if response.ok:
                    st.success(f"API responded successfully (HTTP {response.status_code}).")
                    try:
                        st.json(response.json())
                    except ValueError:
                        st.text(response.text[:3000] or "(Empty response)")
                else:
                    st.error(f"API returned HTTP {response.status_code}.")
                    st.text(response.text[:1500])
            except requests.RequestException as exc:
                st.error("Could not reach the API.")
                st.caption(str(exc))
        st.caption(
            "The health route shown here follows the route documented for the "
            "Hugging Face Spaces deployment. If your deployment uses another "
            "health endpoint, update the path in streamlit_app/app.py."
        )

st.markdown("---")
st.caption("CortexAI • Keep API keys and service credentials in deployment secrets, never in source code.")
