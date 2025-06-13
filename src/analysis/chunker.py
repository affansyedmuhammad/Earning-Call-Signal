import json
import re
from pathlib import Path
from typing import List, Tuple

# Regex to split at speaker-label boundaries (e.g. "Operator:", "Jensen Huang:")
# Use double quotes for raw string and escape apostrophe correctly
SPEAKER_SPLIT_PATTERN = re.compile(r"(?m)(?=^[A-Za-z][\w \(\)&'-]+: )")


def chunk_by_speaker(text: str) -> List[str]:
    """
    Splits a transcript into chunks by speaker-turn, preserving the speaker label.
    """
    raw_chunks = SPEAKER_SPLIT_PATTERN.split(text)
    return [c.strip() for c in raw_chunks if c.strip()]


def load_and_chunk(filepath: Path) -> List[Tuple[str, str]]:
    """
    Reads the file at `filepath`, handles JSON or plain text,
    unescapes literal "\\n" to real newlines,
    and returns a list of (speaker, chunk_text).
    """
    # Read raw file content
    content = filepath.read_text(encoding='utf-8')

    # Try parsing JSON to extract 'transcript' field
    try:
        data = json.loads(content)
        transcript = data.get('transcript', '')
        # Convert literal "\n" sequences into actual newlines
        transcript = transcript.replace('\\n', '\n')
    except json.JSONDecodeError:
        transcript = content

    # Split into speaker turns
    raw_chunks = chunk_by_speaker(transcript)
    out: List[Tuple[str, str]] = []
    for c in raw_chunks:
        speaker, _, body = c.partition(': ')
        out.append((speaker, body.strip()))
    return out
