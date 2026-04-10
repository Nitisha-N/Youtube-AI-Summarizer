from typing import List


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping word-based chunks.
    Overlap ensures context is preserved across chunk boundaries.
    Returns list of chunk strings.
    """
    words = text.split()
    total_words = len(words)

    if total_words <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < total_words:
        end = min(start + chunk_size, total_words)
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == total_words:
            break
        start += chunk_size - overlap  # step back by overlap for continuity

    return chunks
