#!/bin/bash
# Fish Audio Bridge Patch
# Patcht die nanobot WhatsApp Bridge für Audio-Support (Senden & Empfangen)
# Verwendung: bash patch-bridge.sh
# Sicher erneut ausführbar (idempotent)

set -e

BRIDGE_DIR="$HOME/.nanobot/bridge/dist"
WA_FILE="$BRIDGE_DIR/whatsapp.js"
SRV_FILE="$BRIDGE_DIR/server.js"
NANOBOT_PKG="$HOME/.local/share/uv/tools/nanobot-ai/lib/python3.12/site-packages/nanobot"
WA_PY="$NANOBOT_PKG/channels/whatsapp.py"

echo "🔧 Fish Audio Bridge Patch"
echo "=========================="

# Check if bridge exists
if [ ! -f "$WA_FILE" ]; then
    echo "❌ Bridge nicht gefunden: $WA_FILE"
    echo "   Bitte zuerst 'nanobot channels login' ausführen."
    exit 1
fi

# ============================================================
# PATCH 1: whatsapp.js - Audio Download (Empfangen)
# ============================================================
echo "📥 Patch 1: Audio-Download aktivieren..."

if grep -q "unwrapped.audioMessage" "$WA_FILE" && grep -q "downloadMedia.*audioMessage" "$WA_FILE"; then
    echo "   ✅ Audio-Download bereits gepatcht"
else
    # Add audioMessage download block after videoMessage block
    sed -i '/else if (unwrapped\.videoMessage) {/,/}$/!b; /}$/{
        a\                else if (unwrapped.audioMessage) {\
                    fallbackContent = '"'"'[Voice Message]'"'"';\
                    const path = await this.downloadMedia(msg, unwrapped.audioMessage.mimetype ?? '"'"'audio/ogg'"'"');\
                    if (path)\
                        mediaPaths.push(path);\
                }
    }' "$WA_FILE"
    echo "   ✅ Audio-Download hinzugefügt"
fi

# ============================================================
# PATCH 2: whatsapp.js - Audio Senden
# ============================================================
echo "📤 Patch 2: Audio-Senden aktivieren..."

if grep -q "sendAudio" "$WA_FILE"; then
    echo "   ✅ sendAudio bereits vorhanden"
else
    # Add sendAudio method before disconnect method
    sed -i '/async disconnect()/i\    async sendAudio(to, audioPath) {\
        if (!this.sock) {\
            throw new Error('"'"'Not connected'"'"');\
        }\
        const { readFile } = await import('"'"'fs/promises'"'"');\
        const buffer = await readFile(audioPath);\
        await this.sock.sendMessage(to, {\
            audio: buffer,\
            mimetype: '"'"'audio/ogg; codecs=opus'"'"',\
            ptt: true\
        });\
    }' "$WA_FILE"
    echo "   ✅ sendAudio Methode hinzugefügt"
fi

# ============================================================
# PATCH 3: server.js - Audio Command Handler
# ============================================================
echo "🔌 Patch 3: Server Audio-Command..."

if grep -q "send_audio" "$SRV_FILE"; then
    echo "   ✅ send_audio Command bereits vorhanden"
else
    sed -i '/await this\.wa\.sendMessage(cmd\.to, cmd\.text);/a\        }\n        else if (cmd.type === '"'"'send_audio'"'"' \&\& this.wa) {\n            await this.wa.sendAudio(cmd.to, cmd.audioPath);' "$SRV_FILE"
    echo "   ✅ send_audio Command hinzugefügt"
fi

# ============================================================
# PATCH 4: whatsapp.py - Voice Message Handling
# ============================================================
echo "🐍 Patch 4: Python Voice Message Handler..."

if [ ! -f "$WA_PY" ]; then
    echo "   ⚠️  whatsapp.py nicht gefunden: $WA_PY"
    echo "   Überspringe Python-Patch."
else
    if grep -q "Transcription not available" "$WA_PY"; then
        # Replace the "not available" block with a pass-through that keeps [Voice Message]
        # so the media path gets attached and the skill can handle transcription
        sed -i 's/content = "\[Voice Message: Transcription not available for WhatsApp yet\]"/pass  # Fish Audio patch: voice handled via media path + skill/' "$WA_PY"
        sed -i 's/logger.info("Voice message received from {}, but direct download from bridge is not yet supported.", sender_id)/logger.info("Voice message received from {}, processing via Fish Audio skill.", sender_id)/' "$WA_PY"
        echo "   ✅ Python Voice Handler gepatcht"
    else
        echo "   ✅ Python Voice Handler bereits gepatcht"
    fi

    # Add audio media type detection
    if grep -q '"audio" if mime' "$WA_PY"; then
        echo "   ✅ Audio media type bereits vorhanden"
    else
        sed -i 's/media_type = "image" if mime and mime.startswith("image\/") else "file"/media_type = "image" if mime and mime.startswith("image\/") else ("audio" if mime and mime.startswith("audio\/") else "file")/' "$WA_PY"
        echo "   ✅ Audio media type hinzugefügt"
    fi
fi

echo ""
echo "✅ Bridge-Patch abgeschlossen!"
echo "   Bitte Services neu starten:"
echo "   systemctl --user restart nanobot-channels"
echo "   systemctl --user restart nanobot-gateway"
