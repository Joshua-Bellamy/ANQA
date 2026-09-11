<div align="center">
  <img src="app/static/logo.png" alt="ANQA Logo" width="180">

  # ANQA — Reborn Intelligence
  
  **A multimodal AI assistant with long-term memory**
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![OpenRouter](https://img.shields.io/badge/OpenRouter-191919?style=for-the-badge&logo=openai&logoColor=white)](https://openrouter.ai/)
</div>

<br>

Anqa is a multimodal AI assistant featuring long-term memory, voice input/output, and robust support for images, videos, PDFs, and general file attachments. Built on top of **FastAPI** and **OpenRouter**, it is designed for scale, modularity, and high performance.

---

## 🏛️ Why This Architecture?

Most chatbot projects are a single script that calls an LLM API. Anqa is built as a **production-ready service**. Every concern (authentication, chat orchestration, memory, file ingestion, voice) lives in its own isolated module, ensuring the codebase reads and scales like enterprise software, not a demo script.

```text
app/
├── core/
│   ├── config.py           # Settings loaded once from environment variables
│   └── security.py         # JWT authentication
├── models/
│   └── schemas.py          # Centralized request/response contracts
├── services/
│   ├── openrouter_client.py # LLM communication layer
│   ├── ingestion.py        # File storage & PDF text extraction
│   └── voice.py            # STT/TTS provider integrations
├── memory/
│   └── store.py            # Long-term vector memory (ChromaDB)
├── routers/
│   ├── chat.py             # POST /chat/send (streaming enabled)
│   ├── upload.py           # POST /upload (images/video/pdf/files)
│   └── voice.py            # POST /voice/transcribe, POST /voice/speak
└── main.py                 # Application entrypoint
