"""
app/services/voice.py

Provider calls for speech-to-text and text-to-speech. Written against
the OpenAI-compatible Whisper/TTS API shape since that's the most
widely mirrored interface — swapping to a different provider means
editing only this file.

Note: requires settings.stt_api_key / settings.tts_api_key to be set.
If you don't want to pay for a separate STT/TTS key yet, this module
is the one piece of Anqa you can leave disabled while everything else
(chat, memory, file upload) works fully.
"""

from collections.abc import AsyncGenerator

import httpx

from app.core.config import settings

_STT_URL = "https://api.openai.com/v1/audio/transcriptions"
_TTS_URL = "https://api.openai.com/v1/audio/speech"


async def transcribe_audio(audio_bytes: bytes, filename: str) -> dict:
    if not settings.stt_api_key:
        raise RuntimeError("STT_API_KEY not configured — voice input is disabled")

    headers = {"Authorization": f"Bearer {settings.stt_api_key}"}
    files = {"file": (filename, audio_bytes)}
    data = {"model": "whisper-1"}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(_STT_URL, headers=headers, files=files, data=data)
        resp.raise_for_status()
        result = resp.json()

    return {"text": result.get("text", ""), "language": result.get("language")}


async def synthesize_speech(text: str, voice: str = "alloy") -> AsyncGenerator[bytes, None]:
    if not settings.tts_api_key:
        raise RuntimeError("TTS_API_KEY not configured — voice output is disabled")

    headers = {"Authorization": f"Bearer {settings.tts_api_key}"}
    payload = {"model": "tts-1", "voice": voice, "input": text}

    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", _TTS_URL, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            async for chunk in resp.aiter_bytes():
                yield chunk
