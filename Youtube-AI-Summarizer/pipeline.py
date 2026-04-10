"""
Core pipeline: YouTube URL → Transcript → Summary → Article
No external orchestration dependencies (Prefect/MLflow removed for simplicity).
"""
import time
from dataclasses import dataclass
from typing import Optional

from src.transcript import fetch_transcript
from src.chunking import chunk_text
from src.summarizer import summarize
from src.article import generate_article
from src.llm_client import GeminiClient
from src.utils import load_config, extract_video_id, md_to_html, estimate_read_time


@dataclass
class PipelineResult:
    video_id: str
    transcript_length: int
    chunk_count: int
    tldr: str
    article_md: str
    article_html: str
    read_time_minutes: int
    elapsed_seconds: float


def run_pipeline(
    url: str,
    api_key: str,
    tone: str = "professional",
    audience: str = "general readers",
    config_path: str = "config/config.yaml"
) -> PipelineResult:
    """
    End-to-end pipeline from YouTube URL to structured article.
    Returns a PipelineResult with all outputs and metadata.
    """
    start = time.time()
    cfg = load_config(config_path)

    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Could not extract a valid YouTube video ID from: {url}")

    # Build LLM client
    llm = GeminiClient(
        api_key=api_key,
        model_name=cfg['model']['name'],
        temperature=cfg['model']['temperature'],
        max_tokens=cfg['model'].get('max_output_tokens', 2048)
    )

    # Stage 1: Fetch transcript
    transcript = fetch_transcript(video_id)

    # Stage 2: Chunk
    chunks = chunk_text(
        transcript,
        chunk_size=cfg['chunking']['chunk_size'],
        overlap=cfg['chunking'].get('overlap', 50)
    )

    # Stage 3: Summarize
    tldr = summarize(chunks, llm)

    # Stage 4: Generate article
    article_md = generate_article(tldr, llm, tone=tone, audience=audience)

    # Stage 5: Convert formats
    article_html = md_to_html(article_md)
    read_time = estimate_read_time(article_md)
    elapsed = round(time.time() - start, 1)

    return PipelineResult(
        video_id=video_id,
        transcript_length=len(transcript.split()),
        chunk_count=len(chunks),
        tldr=tldr,
        article_md=article_md,
        article_html=article_html,
        read_time_minutes=read_time,
        elapsed_seconds=elapsed
    )
