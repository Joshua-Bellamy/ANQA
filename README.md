# Anqa

A multimodal AI assistant with long-term memory — voice input/output, and
support for images, videos, PDFs, and general file attachments — built on
FastAPI and OpenRouter.

## Why this architecture

Most chatbot projects are a single file that calls an LLM API. Anqa is
built as a real service: every concern (auth, chat orchestration, memory,
file ingestion, voice) lives in its own module, so the codebase reads like
production software, not a demo script.

```
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
```

## What makes the memory "powerful"

Most chatbot memory is just "resend the last N messages." Anqa instead:

1. Summarizes each exchange and embeds it into a vector store (`app/memory/store.py`)
2. On every new message, retrieves the most semantically relevant past
   memories for that user — even from conversations days or weeks old
3. Injects only the relevant memories into the system prompt, instead of
   dumping full chat history (keeps token usage low and answers focused)

This means the assistant can recall something the user mentioned in a
completely different conversation, without the user having to repeat it.

## Multimodal input

- **Images**: sent to OpenRouter's vision-capable models using the
  OpenAI-compatible `image_url` content format (`openrouter_client.py`)
- **PDFs**: text is extracted server-side (`ingestion.py`) and given to
  the model as context, since most LLMs can't read raw PDF bytes
- **Video / general files**: stored and referenced by URL; a video
  frame-extraction + PDF-OCR fallback are natural next additions (see
  "Next steps" below) — the ingestion module is built so those slot in
  without touching any router

## Voice

STT (speech-to-text) and TTS (text-to-speech) are isolated in
`app/services/voice.py` behind a simple interface, so the app runs fully
without voice configured, and voice can be swapped to a different
provider by editing one file.

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in OPENROUTER_API_KEY and JWT_SECRET_KEY
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API docs.

## Deploying

The included `Dockerfile` runs as-is on any container platform with a
free tier (Render, Fly.io, Railway). No paid/KYC-gated infra required —
OpenRouter's key is pay-as-you-go and the vector store/database are both
local files by default.

## Next steps (roadmap)

- [ ] Frontend web client (chat UI, file/voice upload)
- [ ] Conversation history persistence (SQLAlchemy models + endpoints)
- [ ] Video: extract keyframes and send to the vision model
- [ ] PDF OCR fallback for scanned documents
- [ ] Background memory summarization job (batch, not per-message)
- [ ] Tests (`tests/`)
- [ ] CI (GitHub Actions: lint + test on push)
