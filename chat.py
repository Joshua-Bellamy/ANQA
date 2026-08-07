"""
app/routers/chat.py

The core chat endpoint. This is where a user turn becomes a model turn:
1. Retrieve relevant long-term memories for this user.
2. Build the message list (system prompt + memories + recent history + new turn).
3. Stream the completion back to the client over SSE.
4. After the turn completes, store a summarized memory for next time.

Kept intentionally thin: all real logic (LLM calls, memory) lives in
app/services and app/memory — this file only orchestrates.
"""

import json
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.security import get_current_user_id
from app.memory.store import memory_store
from app.models.schemas import ChatMessageIn
from app.services.openrouter_client import openrouter_client

router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_PROMPT = (
    "You are Anqa, a helpful, precise AI assistant with long-term memory "
    "of the user. Use the MEMORY block below only if it's relevant to the "
    "current message; otherwise ignore it."
)


def _build_messages(user_text: str, memories: list[dict], image_urls: list[str]) -> list[dict]:
    memory_block = "\n".join(f"- {m['text']}" for m in memories) or "(no relevant memories)"
    system = f"{SYSTEM_PROMPT}\n\nMEMORY:\n{memory_block}"
    messages = [{"role": "system", "content": system}]
    messages.append(openrouter_client.build_user_message(user_text, image_urls))
    return messages


@router.post("/send")
async def send_message(
    payload: ChatMessageIn,
    user_id: str = Depends(get_current_user_id),
):
    """
    Send a message and stream the assistant's reply back as
    Server-Sent Events. Each event is a JSON chunk: {"delta": "..."}.
    """
    conversation_id = payload.conversation_id or str(uuid.uuid4())

    # Step 1: pull relevant long-term memory for this user
    memories = memory_store.retrieve(user_id=user_id, query=payload.content)

    # Step 2: resolve attachment_ids -> image URLs
    # (attachment lookup delegated to app/services/uploads.py — omitted here
    #  for brevity; see that module for the resolve_attachments() helper)
    image_urls: list[str] = []

    messages = _build_messages(payload.content, memories, image_urls)

    async def event_stream():
        full_reply = ""
        async for raw_chunk in openrouter_client.chat_completion_stream(
            messages, has_images=bool(image_urls)
        ):
            try:
                chunk = json.loads(raw_chunk)
                delta = chunk["choices"][0]["delta"].get("content", "")
            except (KeyError, IndexError, json.JSONDecodeError):
                continue
            if delta:
                full_reply += delta
                yield f"data: {json.dumps({'delta': delta})}\n\n"

        # Step 3: after the full reply is in, store a memory of this exchange
        if payload.content and full_reply:
            summary = f"User asked: {payload.content[:200]} | Assistant replied: {full_reply[:200]}"
            memory_store.add_memory(user_id=user_id, text=summary, conversation_id=conversation_id)

        yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
