import os
import tempfile

import markdown as md_lib
import streamlit as st

from pipeline import run_pipeline
from src.pdf import make_pdf

# Page configiguration
st.set_page_config(
    page_title="YouTube to Article",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load API key
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    API_KEY = None

# Minimal CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .stApp {
        background-color: #f8f7f4;
        color: #1a1a1a;
    }
    .stButton > button {
        background-color: #1a1a1a;
        color: #f8f7f4;
        border: none;
        border-radius: 4px;
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        padding: 0.6rem 1.6rem;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #333333;
        color: #f8f7f4;
    }
    .stDownloadButton > button {
        background-color: #f8f7f4;
        color: #1a1a1a;
        border: 1px solid #cccccc;
        border-radius: 4px;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.88rem;
        width: 100%;
    }
    .stDownloadButton > button:hover {
        border-color: #1a1a1a;
    }
    h1, h2, h3 {
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 600;
        color: #1a1a1a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Guard: stop if no API key is configured
if API_KEY is None:
    st.error(
        "No Gemini API key found. "
        "Open .streamlit/secrets.toml and set GEMINI_API_KEY = your key, then restart."
    )
    st.stop()

# Header
st.title("YouTube to Article")
st.caption("Paste a YouTube URL to generate a structured article powered by Gemini.")
st.divider()

# Input section
url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
)

col_left, col_right = st.columns(2)

with col_left:
    tone = st.selectbox(
        "Writing Tone",
        ["Professional", "Conversational", "Academic", "Journalistic", "Beginner-friendly"],
    )

with col_right:
    audience = st.selectbox(
        "Target Audience",
        ["General readers", "Business professionals", "Students", "Researchers", "Tech enthusiasts"],
    )

run_button = st.button("Generate Article", use_container_width=True)

st.divider()

# Run pipeline when button is clicked
if run_button:
    if not url.strip():
        st.warning("Please paste a YouTube URL before generating.")
    else:
        # Clear any previous result so stale content is never shown
        st.session_state.pop("result", None)
        st.session_state.pop("error", None)

        with st.spinner("Fetching transcript and generating article..."):
            try:
                result = run_pipeline(
                    url=url.strip(),
                    api_key=API_KEY,
                    tone=tone.lower(),
                    audience=audience.lower(),
                )
                st.session_state["result"] = result
            except ValueError as exc:
                st.session_state["error"] = str(exc)
            except RuntimeError as exc:
                st.session_state["error"] = f"LLM error: {str(exc)}"
            except Exception as exc:
                st.session_state["error"] = f"Unexpected error: {str(exc)}"

# Show error if one was stored
if "error" in st.session_state:
    st.error(st.session_state["error"])

# Show results if a result is stored
if "result" in st.session_state:
    result = st.session_state["result"]

    # Pipeline stats in a clean metric row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transcript words", f"{result.transcript_length:,}")
    c2.metric("Chunks processed", result.chunk_count)
    c3.metric("Read time", f"{result.read_time_minutes} min")
    c4.metric("Pipeline time", f"{result.elapsed_seconds}s")

    st.divider()

    # Summary
    st.subheader("Summary")
    st.info(result.tldr)

    st.divider()

    # Article 
    col_article, col_exports = st.columns([3, 1])

    with col_article:
        st.subheader("Article")
        article_html = md_lib.markdown(
            result.article_md,
            extensions=["extra", "sane_lists"],
        )
        st.markdown(article_html, unsafe_allow_html=True)

    with col_exports:
        st.subheader("Export")

        st.download_button(
            label="Download Markdown",
            data=result.article_md,
            file_name="article.md",
            mime="text/markdown",
            use_container_width=True,
        )

        st.download_button(
            label="Download HTML",
            data=result.article_html,
            file_name="article.html",
            mime="text/html",
            use_container_width=True,
        )

        # Generate PDF and offer download
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                pdf_path = tmp.name
            make_pdf(result.article_md, pdf_path)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name="article.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.caption(f"PDF not available: {exc}")
        finally:
            if "pdf_path" in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)

        st.divider()

        with st.expander("Video details"):
            st.write(f"Video ID: {result.video_id}")
            st.write(f"YouTube link: https://www.youtube.com/watch?v={result.video_id}")
            st.write(f"Average chunk: {result.transcript_length // result.chunk_count} words")
