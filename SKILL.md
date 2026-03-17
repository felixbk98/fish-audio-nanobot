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

- **API Key:** `FISHAUDIO_API_KEY` als Umgebungsvariable (z.B. in `~/.config/environment.d/fishaudio.conf`)
- **Einstellungen:** `config.json` im Skill-Ordner
  - `voice_id` — Fish Audio Stimmen-ID
  - `tts_format` — Audio-Format (Standard: mp3)
  - `tts_bitrate` — Bitrate für OGG/OPUS (Standard: 64k)
  - `stt_language` — Sprache für STT (Standard: de)
  - `speed` — Sprechgeschwindigkeit (Standard: 1.0, z.B. 1.5 = schneller, 0.8 = langsamer)
- **Python:** Nanobot Python-Pfad (via `$(dirname $(readlink -f $(which nanobot)))/python3`)
- **Skripte:** `scripts/` im Skill-Ordner

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
NANOBOT_PYTHON=$(dirname $(readlink -f $(which nanobot)))/python3
$NANOBOT_PYTHON <skill_dir>/scripts/stt.py "<pfad_zur_audio_datei>"
```

3. Den transkribierten Text als eigentliche User-Nachricht behandeln und darauf antworten.
4. Prüfen ob der User in der Nachricht "antworte als Memo/Sprachnachricht" gesagt hat → dann TTS nutzen.

## Sprachnachricht senden (TTS)

Wenn der User eine Sprachantwort wünscht:

### Schritt 1: Text zu Audio
```bash
NANOBOT_PYTHON=$(dirname $(readlink -f $(which nanobot)))/python3
$NANOBOT_PYTHON <skill_dir>/scripts/tts.py "<antworttext>" "/tmp/nanobot_tts_$(date +%s).ogg"
```
Voice ID wird automatisch aus `config.json` gelesen.

### Schritt 2: Audio senden
```bash
NANOBOT_PYTHON=$(dirname $(readlink -f $(which nanobot)))/python3
$NANOBOT_PYTHON <skill_dir>/scripts/send_audio.py "<chat_id>" "<pfad_zur_ogg_datei>"
```

Die `chat_id` ist die WhatsApp ID des Users (z.B. `123456789@s.whatsapp.net` oder eine LID).

## Bridge-Patch

Die WhatsApp Bridge muss gepatcht sein für Audio-Support. Nach einem nanobot-Update:

```bash
bash <skill_dir>/scripts/patch-bridge.sh
```

## Fehlerbehebung

- **"FISHAUDIO_API_KEY not set"**: Key als Umgebungsvariable setzen, VM rebooten
- **ffmpeg Fehler**: `sudo apt install ffmpeg`
- **Bridge sendet kein Audio**: Patch prüfen mit `grep sendAudio ~/.nanobot/bridge/dist/whatsapp.js`
- **fish-audio-sdk fehlt**: `uv pip install fish-audio-sdk --python $(dirname $(readlink -f $(which nanobot)))/python3`
