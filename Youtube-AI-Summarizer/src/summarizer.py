from typing import List
from .llm_client import GeminiClient

CHUNK_SUMMARY_PROMPT = """You are a precise content analyst. Extract the key ideas from this video transcript excerpt.

Instructions:
- Identify 3-5 specific, substantive points (not generic observations)
- Preserve any named concepts, statistics, frameworks, or unique terminology
- Keep each point under 30 words
- Write in clear, direct language

Transcript excerpt:
{chunk}

Key points:"""


TLDR_PROMPT = """You are a skilled editor synthesizing notes from a video into a crisp TLDR.

Chunk summaries:
{summaries}

Write a TLDR that:
1. Opens with a one-sentence hook capturing the core thesis
2. Covers 4-6 of the most important insights
3. Ends with the practical takeaway or "so what"
4. Uses plain, engaging prose — not bullet points
5. Stays under 200 words

TLDR:"""


def summarize(chunks: List[str], llm: GeminiClient) -> str:
    """
    Two-stage summarization:
    1. Summarize each chunk independently
    2. Synthesize chunk summaries into a single TLDR
    """
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        prompt = CHUNK_SUMMARY_PROMPT.format(chunk=chunk)
        summary = llm.generate(prompt)
        chunk_summaries.append(f"[Part {i+1}]\n{summary}")

    combined = "\n\n".join(chunk_summaries)
    tldr = llm.generate(TLDR_PROMPT.format(summaries=combined))
    return tldr
