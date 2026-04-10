from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.formatters import TextFormatter


def fetch_transcript(video_id: str) -> str:
    """
    Fetch transcript for a YouTube video.
    Tries English first, then falls back to auto-generated captions,
    then any available language.
    Returns the full transcript as a single string.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Priority: manual English > auto-generated English > any language
        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
        except Exception:
            pass

        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(['en', 'en-US'])
            except Exception:
                pass

        if transcript is None:
            # Take the first available one and translate to English
            for t in transcript_list:
                transcript = t
                if transcript.is_translatable:
                    transcript = transcript.translate('en')
                break

        if transcript is None:
            raise ValueError("No transcript could be found for this video.")

        entries = transcript.fetch()
        full_text = " ".join(entry['text'] for entry in entries)
        # Clean up common transcript artifacts
        full_text = full_text.replace('\n', ' ').replace('  ', ' ').strip()
        return full_text

    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise ValueError("No transcript found. The video may not have captions.")
    except Exception as e:
        raise ValueError(f"Failed to fetch transcript: {str(e)}")
