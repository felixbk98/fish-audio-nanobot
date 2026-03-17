#!/usr/bin/env python3
"""Fish Audio Text-to-Speech: Converts text to OGG/OPUS audio for WhatsApp."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def text_to_audio(text: str, output_path: str) -> str:
    """Convert text to OGG/OPUS audio file using Fish Audio TTS API."""
    from fishaudio import FishAudio
    from fishaudio.utils import save

    api_key = os.environ.get("FISHAUDIO_API_KEY", "")
    if not api_key:
        print("Error: FISHAUDIO_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    voice_id = config.get("voice_id", "")
    if not voice_id:
        print("Error: voice_id not set in config.json", file=sys.stderr)
        sys.exit(1)

    speed = config.get("speed", 1.0)

    client = FishAudio(api_key=api_key)

    # Generate audio from Fish Audio
    tmp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp_mp3.close()

    try:
        audio = client.tts.convert(
            text=text,
            reference_id=voice_id,
            format=config.get("tts_format", "mp3"),
            speed=speed,
        )
        save(audio, tmp_mp3.name)

        # Convert to OGG/OPUS for WhatsApp voice messages
        bitrate = config.get("tts_bitrate", "64k")
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", tmp_mp3.name,
                    "-c:a", "libopus", "-b:a", bitrate,
                    "-vbr", "on", "-compression_level", "10",
                    output_path,
                ],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg error: {e.stderr.decode()}", file=sys.stderr)
            sys.exit(1)

        return output_path
    finally:
        if os.path.exists(tmp_mp3.name):
            os.unlink(tmp_mp3.name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: tts.py <text> [output_path]", file=sys.stderr)
        sys.exit(1)

    text = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/jarvis_tts.ogg"

    result = text_to_audio(text, output_path)
    print(result)
