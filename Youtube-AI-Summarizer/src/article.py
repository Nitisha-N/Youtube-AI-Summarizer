from .llm_client import GeminiClient

ARTICLE_PROMPT = """You are a professional content writer transforming a video summary into a polished, structured article.

Summary of the video:
{summary}

Write a complete article in Markdown with this exact structure:

# [Compelling, specific title — not generic]

## Introduction
[2-3 paragraphs that hook the reader, introduce the topic, and preview what they'll learn]

## [Theme Section 1 — specific heading]
[2-3 paragraphs expanding on a key idea from the video]

## [Theme Section 2 — specific heading]
[2-3 paragraphs expanding on another key idea]

## [Theme Section 3 — specific heading (add more if needed)]
[2-3 paragraphs]

## Key Takeaways
- [Actionable insight 1]
- [Actionable insight 2]
- [Actionable insight 3]
- [Actionable insight 4]
- [Actionable insight 5]

## Conclusion
[1-2 paragraphs that wrap up the ideas and leave the reader with something to think about]

Rules:
- Write in a clear, engaging {tone} tone suitable for {audience}
- Every section must add value — no filler or repetition
- Use specific details from the summary, not vague generalities
- The article should be 600-900 words total
"""


def generate_article(summary: str, llm: GeminiClient,
                     tone: str = "professional", audience: str = "general readers") -> str:
    """
    Generate a structured Markdown article from the TLDR summary.
    """
    prompt = ARTICLE_PROMPT.format(summary=summary, tone=tone, audience=audience)
    return llm.generate(prompt)
