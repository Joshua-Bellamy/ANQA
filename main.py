"""
app/main.py

The FastAPI application entrypoint. This file should stay small —
its only job is to create the app, attach middleware, and include
routers. All real logic lives in app/routers, app/services, app/memory.

Run locally with:
    uvicorn app.main:app --reload

Deploy the same way on Render/Fly.io/Railway — see Dockerfile.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.routers import chat, upload, voice

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Anqa — a multimodal AI assistant with long-term memory.",
)


@app.on_event("startup")
async def on_startup():
    # Creates the conversations/messages tables if they don't exist yet.
    await init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files back out (images/PDFs referenced in chat)
app.mount("/files", StaticFiles(directory=settings.upload_dir, check_dir=False), name="files")

app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(voice.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
