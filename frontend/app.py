# frontend/streamlit_app.py
import streamlit as st
import requests
import time

# --- Page setup
st.set_page_config(
    page_title="⚡ Text Summarizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (blue / purple tones)
st.markdown("""
    <style>
    body {
        font-family: 'Poppins', sans-serif;
        background-color: #f5f7fb;
    }
    .stApp {
        background-color: #f5f7fb;
    }
    .stButton>button {
        background-color: #4a6cf7; /* blue */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-size: 16px;
        font-weight: 500;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #3b5ad6; /* darker blue */
    }
    .stTextArea textarea {
        border-radius: 10px;
        background-color: #ffffff;
        font-size: 16px;
        padding: 1rem;
        border: 1px solid #cfd8ef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stRadio > label {
        color: #2b2b2b;
        font-weight: 500;
    }
    .stSidebar {
        background-color: #ffffff;
        border-right: 1px solid #e0e6f1;
    }
    .stSidebar header {
        color: #4a6cf7;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1e1e2f;
    }
    .block-container {
        padding-top: 2rem;
    }
    footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Section
st.title("🧠 Text Summarizer")
st.markdown("Summarize long articles quickly using **BART** or **T5** models with a FastAPI backend.")

# --- Sidebar Controls
with st.sidebar:
    st.header("⚙️ Settings")
    model_choice = st.radio("Choose Model:", ["BART", "T5"], horizontal=True)
    max_len = st.slider("Max Summary Length", 50, 300, 130)
    min_len = st.slider("Min Summary Length", 10, 100, 30)
    API_URL = "http://127.0.0.1:8000/summarize"
    st.markdown("---")
    st.info("💡 Tip: Keep input under 1024 tokens for best results.")

# --- Text Input
text_input = st.text_area("✍️ Paste your text below:", height=250, placeholder="Enter or paste an article here...")

# --- Cache API Response
@st.cache_data(show_spinner=False)
def generate_summary(text, model_name, max_len, min_len):
    payload = {
        "text": text,
        "model_name": model_name.lower(),
        "max_length": max_len,
        "min_length": min_len
    }
    response = requests.post(API_URL, json=payload, timeout=120)
    return response

# --- Summary Button
if st.button("🚀 Generate Summary"):
    if not text_input.strip():
        st.warning("⚠️ Please enter text to summarize.")
    else:
        try:
            with st.spinner("⏳ Summarizing..."):
                start_time = time.time()
                response = generate_summary(text_input, model_choice, max_len, min_len)
                elapsed = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                st.subheader("📝 Summary")
                st.success(result["summary"])
            else:
                st.error("❌ API Error! Please check backend logs.")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Try shorter text or smaller summary length.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
