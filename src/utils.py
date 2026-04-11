import re
import yaml
import markdown
from typing import Optional
from urllib.parse import urlparse, parse_qs


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract a YouTube video ID from any supported URL format:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - VIDEO_ID (plain 11-character ID)
    """
    url = url.strip()

    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url

    try:
        parsed = urlparse(url)

        if parsed.netloc in ("youtu.be", "www.youtu.be"):
            return parsed.path.lstrip("/").split("?")[0]

        if "youtube.com" in parsed.netloc:
            if parsed.path == "/watch":
                qs = parse_qs(parsed.query)
                return qs.get("v", [None])[0]
            match = re.match(r"/(embed|v|shorts)/([a-zA-Z0-9_-]{11})", parsed.path)
            if match:
                return match.group(2)
    except Exception:
        pass

    return None


def md_to_html(md_text: str, title: str = "Article") -> str:
    """Convert Markdown text to a complete, styled HTML page."""
    content = markdown.markdown(md_text, extensions=["extra", "sane_lists"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      font-family: Georgia, serif;
      max-width: 780px;
      margin: 60px auto;
      padding: 0 24px;
      color: #1a1a1a;
      line-height: 1.75;
      font-size: 18px;
    }}
    h1 {{ font-size: 2.2em; line-height: 1.2; margin-bottom: 0.3em; }}
    h2 {{ font-size: 1.4em; margin-top: 2em; border-bottom: 2px solid #e5e5e5; padding-bottom: 6px; }}
    p {{ margin: 1em 0; }}
    ul {{ margin: 1em 0; padding-left: 1.4em; }}
    li {{ margin: 0.5em 0; }}
  </style>
</head>
<body>
{content}
</body>
</html>"""


def estimate_read_time(text: str) -> int:
    """Estimate reading time in minutes at 200 words per minute."""
    return max(1, round(len(text.split()) / 200))
