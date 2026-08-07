"""
app/routers/voice.py

Voice I/O for Anqa: upload an audio clip -> get a transcript (STT), or
send text -> get back synthesized speech (TTS). The actual provider
calls live in app/services/voice.py so this router stays provider-agnostic
(swap Whisper for another STT engine without touching this file).
"""

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse

from app.core.security import get_current_user_id
from app.models.schemas import TranscriptionOut, TTSRequest
from app.services.voice import synthesize_speech, transcribe_audio

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/transcribe", response_model=TranscriptionOut)
async def transcribe(
    audio: UploadFile,
    user_id: str = Depends(get_current_user_id),
):
    contents = await audio.read()
    result = await transcribe_audio(contents, filename=audio.filename or "audio.wav")
    return TranscriptionOut(**result)


@router.post("/speak")
async def speak(
    payload: TTSRequest,
    user_id: str = Depends(get_current_user_id),
):
    audio_stream = synthesize_speech(payload.text, voice=payload.voice)
    return StreamingResponse(audio_stream, media_type="audio/mpeg")
