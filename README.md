<div align="center">
  <img src="رابط_الصورة_هنا" alt="Anqa Logo" width="200">
</div>

# Anqa

A multimodal AI assistant with long-term memory — voice input/output, and
support for images, videos, PDFs, and general file attachments — built on
FastAPI and OpenRouter.

## Why this architecture

Most chatbot projects are a single file that calls an LLM API. Anqa is
built as a real service: every concern (auth, chat orchestration, memory,
file ingestion, voice) lives in its own module, so the codebase reads like
production software, not a demo script.

```text
app/
  core/
    config.py      -> all settings, loaded once from environment variables
    security.py    -> JWT auth
  models/
    schemas.py      -> every request/response contract, in one place
  services/
    openrouter_client.py  -> the only file that talks to the LLM
    ingestion.py           -> file storage + PDF text extraction
    voice.py                -> STT/TTS provider calls
  memory/
    store.py        -> long-term vector memory (chromadb)
  routers/
    chat.py          -> POST /chat/send (streaming)
    upload.py         -> POST /upload (images/video/pdf/files)
    voice.py           -> POST /voice/transcribe, POST /voice/speak
  main.py            -> app entrypoint, wires everything together
