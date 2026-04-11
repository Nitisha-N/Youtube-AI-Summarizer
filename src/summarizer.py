from typing import List
from .llm_client import GeminiClient


CHUNK_PROMPT = """You are a precise content analyst. Extract the key ideas from this transcript excerpt.

Instructions:
- Identify 3 to 5 specific, substantive points
- Preserve any named concepts, statistics, frameworks, or terminology
- Keep each point under 30 words
- Write in clear, direct language

Transcript excerpt:
{chunk}

Key points:"""


TLDR_PROMPT = """You are an editor synthesizing notes from a video into a concise summary.

Chunk summaries:
{summaries}

Write a TLDR that:
1. Opens with one sentence capturing the core argument
2. Covers 4 to 6 of the most important insights
3. Ends with the practical takeaway
4. Uses plain, clear prose (no bullet points)
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
        summary = llm.generate(CHUNK_PROMPT.format(chunk=chunk))
        chunk_summaries.append(f"[Part {i + 1}]\n{summary}")

    combined = "\n\n".join(chunk_summaries)
    return llm.generate(TLDR_PROMPT.format(summaries=combined))
