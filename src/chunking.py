from typing import List


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping word-based chunks.
    Overlap preserves context across chunk boundaries.
    Returns a list of chunk strings.
    """
    words = text.split()
    total = len(words)

    if total <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < total:
        end = min(start + chunk_size, total)
        chunks.append(" ".join(words[start:end]))
        if end == total:
            break
        start += chunk_size - overlap

    return chunks
