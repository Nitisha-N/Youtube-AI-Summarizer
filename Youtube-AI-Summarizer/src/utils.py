import yaml
import re
import markdown
from typing import Optional
from urllib.parse import urlparse, parse_qs


def load_config(path: str) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - VIDEO_ID (plain ID)
    """
    url = url.strip()

    # Plain video ID (11 chars, alphanumeric + - _)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    try:
        parsed = urlparse(url)

        # youtu.be short URLs
        if parsed.netloc in ('youtu.be', 'www.youtu.be'):
            return parsed.path.lstrip('/')

        # youtube.com URLs
        if 'youtube.com' in parsed.netloc:
            if parsed.path == '/watch':
                qs = parse_qs(parsed.query)
                return qs.get('v', [None])[0]
            elif parsed.path.startswith('/embed/') or parsed.path.startswith('/v/'):
                return parsed.path.split('/')[2]
            elif parsed.path.startswith('/shorts/'):
                return parsed.path.split('/')[2]

    except Exception:
        pass

    return None


def md_to_html(md_text: str, title: str = "Article") -> str:
    """Convert Markdown to a complete, styled HTML page."""
    content = markdown.markdown(md_text, extensions=['extra', 'sane_lists'])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      font-family: Georgia, 'Times New Roman', serif;
      max-width: 780px;
      margin: 60px auto;
      padding: 0 24px;
      color: #1a1a1a;
      line-height: 1.75;
      font-size: 18px;
    }}
    h1 {{ font-size: 2.2em; line-height: 1.2; margin-bottom: 0.3em; color: #111; }}
    h2 {{ font-size: 1.4em; margin-top: 2em; color: #222; border-bottom: 2px solid #e5e5e5; padding-bottom: 6px; }}
    p {{ margin: 1em 0; }}
    ul {{ margin: 1em 0; padding-left: 1.4em; }}
    li {{ margin: 0.5em 0; }}
    strong {{ color: #111; }}
    @media print {{
      body {{ margin: 40px; }}
    }}
  </style>
</head>
<body>
{content}
</body>
</html>"""


def md_to_markdown_file(md_text: str) -> str:
    """Return the raw markdown string (for .md export)."""
    return md_text


def estimate_read_time(text: str) -> int:
    """Estimate reading time in minutes (avg 200 words/min)."""
    words = len(text.split())
    return max(1, round(words / 200))
