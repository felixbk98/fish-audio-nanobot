#!/usr/bin/env python3
"""Send an audio file as WhatsApp voice message via the nanobot bridge."""

import asyncio
import json
import sys


async def send_audio(chat_id: str, audio_path: str, bridge_url: str = "ws://localhost:3001"):
    """Send audio file through the WhatsApp bridge WebSocket."""
    import websockets

    async with websockets.connect(bridge_url) as ws:
        payload = {
            "type": "send_audio",
            "to": chat_id,
            "audioPath": audio_path,
        }
        await ws.send(json.dumps(payload))
        # Wait for response
        response = await asyncio.wait_for(ws.recv(), timeout=10)
        data = json.loads(response)
        if data.get("type") == "error":
            print(f"Error: {data.get('error')}", file=sys.stderr)
            sys.exit(1)
        print(f"Audio sent to {chat_id}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: send_audio.py <chat_id> <audio_path>", file=sys.stderr)
        sys.exit(1)

    asyncio.run(send_audio(sys.argv[1], sys.argv[2]))
