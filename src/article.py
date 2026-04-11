from .llm_client import GeminiClient


ARTICLE_PROMPT = """You are a professional content writer turning a video summary into a structured article.

Summary:
{summary}

Write a complete article in Markdown with this exact structure:

# [Specific, compelling title]

## Introduction
[2 to 3 paragraphs that introduce the topic and preview what the reader will learn]

## [Section heading based on a key theme]
[2 to 3 paragraphs expanding on this idea with specific detail]

## [Section heading based on another key theme]
[2 to 3 paragraphs]

## [Add more sections if the content requires it]

## Key Takeaways
- [Actionable insight]
- [Actionable insight]
- [Actionable insight]
- [Actionable insight]
- [Actionable insight]

## Conclusion
[1 to 2 paragraphs that wrap up the ideas and leave the reader with something to act on]

Rules:
- Tone: {tone}
- Audience: {audience}
- Every section must add value, no repetition or filler
- Use specific details from the summary, not vague generalities
- Target length: 600 to 900 words
- Do not use em-dashes
"""


def generate_article(
    summary: str,
    llm: GeminiClient,
    tone: str = "professional",
    audience: str = "general readers",
) -> str:
    """Generate a structured Markdown article from the TLDR summary."""
    prompt = ARTICLE_PROMPT.format(summary=summary, tone=tone, audience=audience)
    return llm.generate(prompt)
