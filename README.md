# YouTube to Article

An end-to-end Generative AI pipeline that transforms any YouTube video into a structured, publish-ready article using Google Gemini.

---

## What It Does

Paste a YouTube URL and the system will:

1. Fetch the video transcript (supports auto-generated captions and multiple languages)
2. Split the transcript into overlapping chunks to preserve context
3. Summarize each chunk, then synthesize a final TLDR
4. Generate a structured Markdown article with introduction, thematic sections, key takeaways, and conclusion
5. Export the result as Markdown, HTML, or PDF

---

## Project Structure

```
YOUTUBE-Summarizer/
├── app.py                  Streamlit application (entry point)
├── pipeline.py             Orchestrates the full pipeline
├── requirements.txt        Python dependencies
├── .gitignore
│
├── src/
│   ├── transcript.py       Fetches YouTube captions with language fallback
│   ├── chunking.py         Splits transcript into overlapping word chunks
│   ├── summarizer.py       Two-stage summarization (chunk then TLDR)
│   ├── article.py          Generates structured Markdown article
│   ├── llm_client.py       Gemini API wrapper
│   ├── pdf.py              Renders Markdown to formatted PDF
│   ├── utils.py            URL parser, HTML exporter, read-time estimator
│   └── __init__.py
│
├── config/
│   └── config.yaml         Model name, temperature, chunk settings
│
└── .streamlit/
    └── secrets.toml        Gemini API key [reference uploaded]
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a Gemini API key

Go to [aistudio.google.com](https://aistudio.google.com) and create a free API key. No billing required to start.

### 3. Add your key

Open `.streamlit/secrets.toml` and replace the placeholder:

```toml
GEMINI_API_KEY = "paste-your-key-here"
```

This file is listed in `.gitignore` and will not be committed to version control.

### 4. Run the app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Configuration

Edit `config/config.yaml` to adjust model behavior:

```yaml
model:
  name: gemini-1.5-flash      # Gemini model to use
  temperature: 0.4             # 0 = deterministic, 1 = creative
  max_output_tokens: 2048

chunking:
  chunk_size: 600              # Words per chunk
  overlap: 50                  # Words shared between adjacent chunks
```

---

## How to Use

1. Paste any YouTube URL into the input field
2. Select a writing tone: Professional, Conversational, Academic, Journalistic, or Beginner-friendly
3. Select a target audience: General readers, Business professionals, Students, Researchers, or Tech enthusiasts
4. Click **Generate Article**
5. Read the TLDR summary and full article in the results panel
6. Download the output as Markdown, HTML, or PDF

---

## Supported Videos

| Video type | Works |
|---|---|
| Manual English captions | Yes |
| Auto-generated English captions | Yes |
| Non-English captions (auto-translated) | Yes |
| Private videos | No |
| Videos with captions disabled | No |

---

## Output Formats

| Format | File | Notes |
|---|---|---|
| Markdown | `article.md` | Works with Notion, GitHub, any CMS |
| HTML | `article.html` | Self-contained styled page, ready to publish |
| PDF | `article.pdf` | Formatted with proper headings, bullets, and bold text |

---

## Pipeline Architecture

```
YouTube URL
    |
    v
src/transcript.py    Fetch captions (manual EN > auto EN > any language, translated)
    |
    v
src/chunking.py      Split into overlapping word chunks (preserves boundary context)
    |
    v
src/summarizer.py    Per-chunk summarization then final TLDR synthesis (two stages)
    |
    v
src/article.py       Generate structured Markdown article (tone and audience aware)
    |
    |---> src/utils.py   Convert to styled HTML
    |---> src/pdf.py     Render to formatted PDF
    v
app.py               Streamlit UI
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| AI Model | Google Gemini 1.5 Flash |
| Transcript | youtube-transcript-api |
| PDF Export | ReportLab |
| HTML Export | Python-Markdown |
| Configuration | PyYAML |
| Secrets | .streamlit/secrets.toml |

---

## Key Design Decisions

**Two-stage summarization** -- Each chunk is summarized independently first, then all summaries are synthesized into a final TLDR. This avoids context overflow on long transcripts.

**Overlapping chunks** -- Adjacent chunks share 50 words. Without overlap, sentences at chunk boundaries lose context, which is a common failure point in naive chunking pipelines.

**Session state for results** -- The app stores the pipeline result in `st.session_state` before Streamlit re-runs the script. This prevents the result from being lost on re-render.

**Secrets in secrets.toml** -- The Gemini API key is stored only in `.streamlit/secrets.toml`, which is gitignored. It is never hardcoded anywhere in the source files.

---

## Dependencies

```
streamlit>=1.32.0
google-generativeai>=0.5.0
youtube-transcript-api>=0.6.2
pyyaml>=6.0
markdown>=3.5
reportlab>=4.1.0
```
