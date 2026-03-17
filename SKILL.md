---
name: fish-audio
description: WhatsApp voice messages via Fish Audio (STT + TTS)
---

# Fish Audio — WhatsApp Sprachnachrichten

## Überblick

Dieser Skill ermöglicht das Empfangen und Senden von WhatsApp-Sprachnachrichten über Fish Audio.

- **STT (Speech-to-Text):** Sprachnachricht → Text (Fish Audio ASR)
- **TTS (Text-to-Speech):** Text → Sprachnachricht (Fish Audio TTS)

## Konfiguration

- **API Key:** `FISHAUDIO_API_KEY` in `/home/jarvis/.config/environment.d/fishaudio.conf`
- **Einstellungen:** `/home/jarvis/.nanobot/workspace/skills/fish-audio/config.json`
  - `voice_id` — Fish Audio Stimmen-ID
  - `tts_format` — Audio-Format (Standard: mp3)
  - `tts_bitrate` — Bitrate für OGG/OPUS (Standard: 64k)
  - `stt_language` — Sprache für STT (Standard: de)
  - `speed` — Sprechgeschwindigkeit (Standard: 1.0, z.B. 1.5 = schneller, 0.8 = langsamer)
- **Python:** `/home/jarvis/.local/share/uv/tools/nanobot-ai/bin/python3`
- **Skripte:** `/home/jarvis/.nanobot/workspace/skills/fish-audio/scripts/`

## Antwort-Logik

| Eingang | Anweisung des Users | Antwort |
|---------|---------------------|---------|
| Sprachnachricht | nichts gesagt | **Text** |
| Sprachnachricht | "antworte als Memo/Sprachnachricht" | **Sprachnachricht** |
| Text | nichts gesagt | **Text** |
| Text | "antworte als Memo/Sprachnachricht" | **Sprachnachricht** |

**Standard ist IMMER Text**, außer der User sagt explizit er will eine Sprachnachricht/Memo.

## Sprachnachricht empfangen (STT)

Wenn eine Nachricht `[Voice Message]` enthält UND ein `[audio: /pfad/datei.ogg]` Tag dabei ist:

1. Den Dateipfad aus dem `[audio: ...]` Tag extrahieren
2. Transkribieren:

```bash
/home/jarvis/.local/share/uv/tools/nanobot-ai/bin/python3 \
  /home/jarvis/.nanobot/workspace/skills/fish-audio/scripts/stt.py \
  "<pfad_zur_audio_datei>"
```

3. Den transkribierten Text als eigentliche User-Nachricht behandeln und darauf antworten.
4. Prüfen ob der User in der Nachricht "antworte als Memo/Sprachnachricht" gesagt hat → dann TTS nutzen.

## Sprachnachricht senden (TTS)

Wenn der User eine Sprachantwort wünscht:

### Schritt 1: Text zu Audio
```bash
/home/jarvis/.local/share/uv/tools/nanobot-ai/bin/python3 \
  /home/jarvis/.nanobot/workspace/skills/fish-audio/scripts/tts.py \
  "<antworttext>" \
  "/tmp/jarvis_tts_$(date +%s).ogg"
```
Voice ID wird automatisch aus `config.json` gelesen.

### Schritt 2: Audio senden
```bash
/home/jarvis/.local/share/uv/tools/nanobot-ai/bin/python3 \
  /home/jarvis/.nanobot/workspace/skills/fish-audio/scripts/send_audio.py \
  "<chat_id>" \
  "<pfad_zur_ogg_datei>"
```

Die `chat_id` ist die WhatsApp LID des Users (z.B. `163178726060229@lid`).

## Bridge-Patch

Die WhatsApp Bridge muss gepatcht sein für Audio-Support. Nach einem nanobot-Update:

```bash
bash /home/jarvis/.nanobot/workspace/skills/fish-audio/scripts/patch-bridge.sh
```

Siehe auch: `/home/jarvis/.nanobot/workspace/docs/UPDATE_MANUAL.md`

## Fehlerbehebung

- **"FISHAUDIO_API_KEY not set"**: Key in environment.d prüfen, VM rebooten
- **ffmpeg Fehler**: `sudo apt install ffmpeg`
- **Bridge sendet kein Audio**: Patch prüfen mit `grep sendAudio ~/.nanobot/bridge/dist/whatsapp.js`
- **fish-audio-sdk fehlt**: `uv pip install fish-audio-sdk --python /home/jarvis/.local/share/uv/tools/nanobot-ai/bin/python3`
