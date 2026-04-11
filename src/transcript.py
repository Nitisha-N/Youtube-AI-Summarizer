from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


def fetch_transcript(video_id: str) -> str:
    """
    Fetch transcript for a YouTube video.
    Priority: manual English > auto-generated English > any available language (translated).
    Returns the full transcript as a plain string.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        transcript = None

        try:
            transcript = transcript_list.find_manually_created_transcript(["en", "en-US", "en-GB"])
        except Exception:
            pass

        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(["en", "en-US"])
            except Exception:
                pass

        if transcript is None:
            for t in transcript_list:
                transcript = t.translate("en") if t.is_translatable else t
                break

        if transcript is None:
            raise ValueError("No transcript could be found for this video.")

        entries = transcript.fetch()
        text = " ".join(entry["text"] for entry in entries)
        text = text.replace("\n", " ").replace("  ", " ").strip()
        return text

    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise ValueError("No transcript found. The video may not have captions enabled.")
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch transcript: {str(e)}")
