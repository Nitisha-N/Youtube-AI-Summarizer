# YouTube AI Content Transformation System

An end-to-end Generative AI system that transforms any YouTube video into structured summaries and publish-ready articles. Comes with **two interfaces** — a browser-based frontend (no install) and a Streamlit desktop app.

---

## Project Structure

```
YT_GenAI_Complete/
│
├── frontend/
│   └── index.html          ← Browser app (Groq API, no Python needed)
│
├── src/
│   ├── transcript.py       ← Fetches YouTube captions (multi-language fallback)
│   ├── chunking.py         ← Splits transcript into overlapping chunks
│   ├── summarizer.py       ← Two-stage summarization (chunk → TLDR)
│   ├── article.py          ← Generates structured Markdown article
│   ├── llm_client.py       ← Gemini API wrapper
│   ├── pdf.py              ← Proper Markdown → PDF renderer
│   ├── utils.py            ← URL parsing, HTML export, helpers
│   └── __init__.py
│
├── config/
│   └── config.yaml         ← Model name, temperature, chunk size
│
├── .streamlit/
│   └── secrets.toml        ← Your Gemini API key (never commit this)
│
├── app.py                  ← Streamlit UI
├── pipeline.py             ← Core pipeline orchestrator
├── requirements.txt        ← Python dependencies
└── README.md
```

---

## Option 1 — Browser App (Recommended, No Install)

Uses **Groq API** (free, no credit card, extremely fast).

### Step 1 — Get a free Groq API key

1. Go to **console.groq.com**
2. Sign up with Google / GitHub / email
3. Click **API Keys** → **Create API Key**
4. Copy the key (shown only once)

### Step 2 — Add your key

Open `frontend/index.html` in any text editor. Find this line near the top of the `<script>` section:

```js
const API_KEY = 'YOUR_GROQ_API_KEY_HERE';
```

Replace the placeholder with your key. Save.

### Step 3 — Run a local server

Browsers block API calls from `file://` URLs. Start a local server in 1 command:

```bash
cd YT_GenAI_Complete
python -m http.server 8080
```

Then open: **http://localhost:8080/frontend/**

> No Python? Use Node: `npx serve frontend/`

### Deploy online

Drag `frontend/index.html` to **netlify.com/drop** and get a live URL instantly.

---

## Option 2 — Streamlit Desktop App

Uses **Gemini API** (Google). Generates full articles with PDF export.

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Get a Gemini API key

Go to **aistudio.google.com** → Get API key (free tier available)

### Step 3 — Add your key

Open `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-key-here"
```

### Step 4 — Run

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## What each interface produces

| Feature | Browser App | Streamlit App |
|---|---|---|
| TL;DR summary | ✅ | ✅ |
| Expandable highlights | ✅ YouTube-style | ❌ |
| Full structured article | ✅ | ✅ |
| Topic tags | ✅ | ❌ |
| Export Markdown | ✅ | ✅ |
| Export HTML | ✅ | ✅ |
| Export PDF | ❌ | ✅ |
| Tone selector | ✅ | ✅ |
| Audience selector | ❌ | ✅ |
| Pipeline stats | ❌ | ✅ |
| API cost | Free (Groq) | Free tier (Gemini) |

---

## Pipeline Architecture (Streamlit / Python)

```
YouTube URL
    │
    ▼
src/transcript.py     Fetches captions — manual EN → auto EN → any language
    │
    ▼
src/chunking.py       Overlapping word chunks (preserves boundary context)
    │
    ▼
src/summarizer.py     Per-chunk bullet summary → final TLDR synthesis
    │
    ▼
src/article.py        Structured Markdown article (tone + audience aware)
    │
    ├──▶ src/utils.py   → styled HTML page
    ├──▶ src/pdf.py     → formatted PDF (headings, bullets, bold)
    └──▶ app.py         → Streamlit UI
```

---

## Configuration (`config/config.yaml`)

```yaml
model:
  name: gemini-1.5-flash     # model to use
  temperature: 0.4            # 0 = deterministic, 1 = creative
  max_output_tokens: 2048

chunking:
  chunk_size: 600             # words per chunk
  overlap: 50                 # words shared between chunks

article:
  default_tone: professional
  default_audience: general
```

---

## Security

- `.streamlit/secrets.toml` is **gitignored** — never commit it
- Your Groq key lives only in `frontend/index.html` locally — don't push that file to a public repo with the key in it
- For a public deployment, use environment variables or a backend proxy

---

## Tech Stack

| Layer | Browser App | Streamlit App |
|---|---|---|
| UI | Vanilla HTML/CSS/JS | Streamlit |
| AI | Groq — Llama 3.3 70B | Google Gemini 1.5 Flash |
| Transcript | kome.ai API + fallback | youtube-transcript-api |
| PDF | — | ReportLab |
| Orchestration | — | Pure Python |
