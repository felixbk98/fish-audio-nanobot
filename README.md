# Fish Audio for Nanobot

WhatsApp voice messages (STT + TTS) for [nanobot](https://github.com/HKUDS/nanobot) using [Fish Audio](https://fish.audio).

## Features

- **Speech-to-Text (STT):** Transcribe incoming WhatsApp voice messages via Fish Audio ASR
- **Text-to-Speech (TTS):** Reply with voice messages using custom Fish Audio voices
- **Smart response logic:** Reply as text by default, voice only when requested
- **Update-safe:** Patch script to re-apply changes after nanobot updates

## Prerequisites

- [nanobot](https://github.com/HKUDS/nanobot) installed and running with WhatsApp
- [ffmpeg](https://ffmpeg.org/) installed (`sudo apt install ffmpeg`)
- Fish Audio API key from [fish.audio/app/api-keys](https://fish.audio/app/api-keys)
- A Fish Audio voice model ID (create one at [fish.audio](https://fish.audio))

## Installation

### 1. Install fish-audio-sdk

```bash
uv pip install fish-audio-sdk --python /home/jarvis/.local/share/uv/tools/nanobot-ai/bin/python3
```

### 2. Copy skill to nanobot workspace

```bash
cp -r . ~/.nanobot/workspace/skills/fish-audio/
```

### 3. Configure API key

```bash
echo 'FISHAUDIO_API_KEY=your_api_key_here' > ~/.config/environment.d/fishaudio.conf
```

### 4. Configure voice

Edit `~/.nanobot/workspace/skills/fish-audio/config.json`:

```json
{
  "voice_id": "your_voice_model_id",
  "tts_format": "mp3",
  "tts_bitrate": "64k",
  "stt_language": "de",
  "speed": 1.0
}
```

### 5. Patch the WhatsApp bridge

```bash
bash ~/.nanobot/workspace/skills/fish-audio/scripts/patch-bridge.sh
```

### 6. Restart services

```bash
systemctl --user restart nanobot-channels
systemctl --user restart nanobot-gateway
```

## How it works

### Incoming voice messages (STT)

The patch makes the WhatsApp bridge download audio messages (like it already does for images/videos). The `stt.py` script converts the audio to WAV and sends it to Fish Audio ASR for transcription.

### Outgoing voice messages (TTS)

The `tts.py` script generates audio via Fish Audio TTS, converts it to OGG/OPUS (WhatsApp format), and `send_audio.py` sends it through the bridge WebSocket.

### Response logic

| Input | User says | Response |
|-------|-----------|----------|
| Voice message | nothing | **Text** |
| Voice message | "reply as voice" | **Voice** |
| Text message | nothing | **Text** |
| Text message | "reply as voice" | **Voice** |

## After nanobot updates

The WhatsApp bridge gets rebuilt on updates, so patches must be re-applied:

```bash
# 1. Stop services
systemctl --user stop nanobot-gateway
systemctl --user stop nanobot-channels

# 2. Rebuild bridge
rm -rf ~/.nanobot/bridge
nanobot channels login
# Scan QR code, wait for connection, keep running

# 3. Re-apply patches (in a second terminal)
bash ~/.nanobot/workspace/skills/fish-audio/scripts/patch-bridge.sh
uv pip install fish-audio-sdk --python /home/jarvis/.local/share/uv/tools/nanobot-ai/bin/python3

# 4. Stop login (Ctrl+C in first terminal)

# 5. Start services
systemctl --user start nanobot-channels
systemctl --user start nanobot-gateway
```

> ⚠️ After major nanobot updates, check if the patch patterns still match the new code.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill instructions for nanobot |
| `config.json` | Voice ID, speed, language settings |
| `scripts/stt.py` | Speech-to-Text via Fish Audio |
| `scripts/tts.py` | Text-to-Speech via Fish Audio |
| `scripts/send_audio.py` | Send audio through bridge WebSocket |
| `scripts/patch-bridge.sh` | Patch WhatsApp bridge for audio support |

## What gets patched

| File | Change |
|------|--------|
| `~/.nanobot/bridge/dist/whatsapp.js` | Audio download + sendAudio method |
| `~/.nanobot/bridge/dist/server.js` | send_audio command handler |
| `nanobot/channels/whatsapp.py` | Voice message handler + audio media type |

## License

MIT
