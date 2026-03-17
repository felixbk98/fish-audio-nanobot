#!/usr/bin/env python3
"""Fish Audio Speech-to-Text: Converts audio file to text."""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


def convert_to_wav(input_path: str) -> str:
    """Convert any audio format to WAV using ffmpeg."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", tmp.name],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error: {e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)
    return tmp.name


def transcribe(audio_path: str) -> str:
    """Transcribe audio file using Fish Audio ASR API."""
    from fishaudio import FishAudio

    api_key = os.environ.get("FISHAUDIO_API_KEY", "")
    if not api_key:
        print("Error: FISHAUDIO_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = FishAudio(api_key=api_key)

    # Convert to WAV if not already
    p = Path(audio_path)
    if p.suffix.lower() not in (".wav",):
        wav_path = convert_to_wav(audio_path)
    else:
        wav_path = audio_path

    try:
        with open(wav_path, "rb") as f:
            result = client.asr.transcribe(audio=f.read(), language="de")
        return result.text
    finally:
        # Clean up temp WAV if we created one
        if wav_path != audio_path and os.path.exists(wav_path):
            os.unlink(wav_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: stt.py <audio_file>", file=sys.stderr)
        sys.exit(1)

    text = transcribe(sys.argv[1])
    print(text)
