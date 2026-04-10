import streamlit as st
import tempfile
import os
import markdown as md_lib
from pipeline import run_pipeline
from src.pdf import make_pdf

# ─── Page config MUST be first Streamlit call ─────────────────────────────────
st.set_page_config(
    page_title="YT → Article",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Load API key from secrets ────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = None

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .stApp { background: #0d0f14; color: #e8e6e1; }
  #MainMenu, footer, header { visibility: hidden; }

  /* Hero */
  .hero { text-align: center; padding: 3.5rem 1rem 2rem; }
  .hero-eyebrow {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.18em;
    text-transform: uppercase; color: #e85d4a; margin-bottom: 0.8rem;
  }
  .hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    line-height: 1.1; color: #f0ede8; margin: 0 0 1rem;
  }
  .hero-sub {
    font-size: 1.05rem; color: #8a8782;
    max-width: 520px; margin: 0 auto 2.5rem; line-height: 1.65;
  }

  /* Inputs */
  .stTextInput > div > div > input,
  .stSelectbox > div > div {
    background: #1e2128 !important;
    border: 1px solid #2e3240 !important;
    border-radius: 10px !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: #e85d4a !important;
    box-shadow: 0 0 0 3px rgba(232,93,74,0.15) !important;
  }
  label { color: #a8a5a0 !important; font-size: 0.85rem !important; font-weight: 500 !important; }

  /* Generate button */
  .stButton > button {
    background: #e85d4a !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 1rem !important; padding: 0.7rem 2.2rem !important;
    transition: all 0.2s !important; width: 100%;
  }
  .stButton > button:hover { background: #d44c39 !important; transform: translateY(-1px) !important; }

  /* Download buttons */
  .stDownloadButton > button {
    background: #1e2128 !important; color: #e8e6e1 !important;
    border: 1px solid #2e3240 !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important;
    width: 100% !important; transition: all 0.2s !important;
  }
  .stDownloadButton > button:hover {
    border-color: #e85d4a !important; color: #e85d4a !important;
    background: #1e2128 !important;
  }

  /* Result tags */
  .result-tag {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; background: #e85d4a22; color: #e85d4a;
    padding: 3px 10px; border-radius: 20px; margin-right: 8px;
  }

  /* TLDR */
  .tldr-box {
    background: #16191f; border-left: 3px solid #e85d4a;
    border-radius: 0 12px 12px 0; padding: 1.4rem 1.6rem;
    color: #c8c5c0; line-height: 1.75; font-size: 1rem;
  }

  /* Article */
  .article-box {
    background: #16191f; border: 1px solid #2a2d35;
    border-radius: 12px; padding: 2rem 2.4rem;
    color: #d0cdc8; line-height: 1.8; font-size: 0.97rem;
  }
  .article-box h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.8rem !important; color: #f0ede8 !important; margin-bottom: 1.2rem !important;
  }
  .article-box h2 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.3rem !important; color: #e8e6e1 !important;
    margin-top: 1.8rem !important; margin-bottom: 0.6rem !important;
    border-bottom: 1px solid #2a2d35 !important; padding-bottom: 6px !important;
  }
  .article-box p { margin-bottom: 1rem !important; }
  .article-box ul { padding-left: 1.4rem; }
  .article-box li { margin-bottom: 0.5rem; }
  .article-box strong { color: #f0ede8; }

  /* Stats */
  .stats-bar {
    display: flex; gap: 2rem; background: #16191f;
    border: 1px solid #2a2d35; border-radius: 10px;
    padding: 1rem 1.6rem; margin-bottom: 2rem; flex-wrap: wrap;
  }
  .stat-item { text-align: center; }
  .stat-value { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: #e85d4a; }
  .stat-label { font-size: 0.75rem; color: #6a6865; text-transform: uppercase; letter-spacing: 0.08em; }

  /* Misc */
  .error-box {
    background: #2a1515; border: 1px solid #5c2020;
    border-radius: 10px; padding: 1.2rem 1.4rem; color: #f08080;
  }
  .success-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0d2a1a; border: 1px solid #1a5c35; color: #4caf50;
    font-size: 0.8rem; font-weight: 600; padding: 4px 12px;
    border-radius: 20px; margin-bottom: 1.5rem;
  }
  hr.divider { border: none; border-top: 1px solid #2a2d35; margin: 2.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">Generative AI · Content Transformation</div>
  <h1 class="hero-title">YouTube → Article</h1>
  <p class="hero-sub">Paste any YouTube URL. Get a polished, publish-ready article in seconds — with TLDR, structured sections, and multi-format export.</p>
</div>
""", unsafe_allow_html=True)

# ─── Missing key guard ────────────────────────────────────────────────────────
if api_key is None:
    st.markdown(
        '<div class="error-box">⚠️ No API key found. '
        'Add <code>GEMINI_API_KEY = "your-key"</code> to '
        '<code>.streamlit/secrets.toml</code> and restart.</div>',
        unsafe_allow_html=True
    )
    st.stop()

# ─── Input form (pure Streamlit — no wrapping divs) ───────────────────────────
url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")

col_tone, col_audience = st.columns(2)
with col_tone:
    tone = st.selectbox("Writing Tone", [
        "professional", "conversational", "academic", "journalistic", "beginner-friendly"
    ])
with col_audience:
    audience = st.selectbox("Target Audience", [
        "general readers", "business professionals", "students", "researchers", "tech enthusiasts"
    ])

generate_clicked = st.button("⚡ Generate Article", use_container_width=True)

st.markdown("---")

# ─── Pipeline ─────────────────────────────────────────────────────────────────
if generate_clicked:
    if not url.strip():
        st.markdown('<div class="error-box">⚠️ Please enter a YouTube URL.</div>', unsafe_allow_html=True)
    else:
        try:
            with st.status("Running pipeline...", expanded=True) as status:
                st.write("📡 Fetching YouTube transcript...")
                result = run_pipeline(
                    url=url,
                    api_key=api_key,
                    tone=tone,
                    audience=audience,
                )
                st.write(f"✅ Transcript fetched — {result.transcript_length:,} words across {result.chunk_count} chunks")
                st.write("🧠 Summary and article generated")
                st.write(f"⏱️ Done in {result.elapsed_seconds}s")
                status.update(label="✅ Pipeline complete!", state="complete")

            st.session_state["result"] = result

        except ValueError as e:
            st.markdown(f'<div class="error-box">⚠️ {e}</div>', unsafe_allow_html=True)
        except RuntimeError as e:
            st.markdown(f'<div class="error-box">🔴 LLM Error: {e}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">🔴 Unexpected error: {e}</div>', unsafe_allow_html=True)

# ─── Results ──────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    result = st.session_state["result"]

    st.markdown('<div class="success-badge">✓ Generated successfully</div>', unsafe_allow_html=True)

    # Stats
    st.markdown(f"""
    <div class="stats-bar">
      <div class="stat-item">
        <div class="stat-value">{result.transcript_length:,}</div>
        <div class="stat-label">Transcript words</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{result.chunk_count}</div>
        <div class="stat-label">Chunks processed</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{result.read_time_minutes} min</div>
        <div class="stat-label">Read time</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{result.elapsed_seconds}s</div>
        <div class="stat-label">Pipeline time</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # TLDR
    st.markdown('<span class="result-tag">TLDR</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="tldr-box">{result.tldr}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Article + exports side by side
    col_article, col_exports = st.columns([2.2, 1])

    with col_article:
        st.markdown('<span class="result-tag">Article</span>', unsafe_allow_html=True)
        article_html_content = md_lib.markdown(result.article_md, extensions=["extra", "sane_lists"])
        st.markdown(f'<div class="article-box">{article_html_content}</div>', unsafe_allow_html=True)

    with col_exports:
        st.markdown('<span class="result-tag">Export</span>', unsafe_allow_html=True)
        st.markdown("####")  # small spacer

        st.download_button(
            "📄 Markdown", data=result.article_md,
            file_name="article.md", mime="text/markdown",
            use_container_width=True,
        )
        st.download_button(
            "🌐 HTML", data=result.article_html,
            file_name="article.html", mime="text/html",
            use_container_width=True,
        )

        # PDF — generate into temp file
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                pdf_path = tmp.name
            make_pdf(result.article_md, pdf_path)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                "📕 PDF", data=pdf_bytes,
                file_name="article.pdf", mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.warning(f"PDF generation failed: {e}")
        finally:
            if "pdf_path" in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)

        with st.expander("ℹ️ Video Info"):
            st.markdown(f"**Video ID:** `{result.video_id}`")
            st.markdown(f"[Open on YouTube ↗](https://youtube.com/watch?v={result.video_id})")
            st.markdown(f"**Avg chunk size:** ≈{result.transcript_length // result.chunk_count} words")
