"""
app/routers/chat.py

The core chat endpoint. This is where a user turn becomes a model turn:
1. Resolve any attachment_ids into usable image URLs.
2. Retrieve relevant long-term memories for this user.
3. Load recent messages in this conversation (short-term history).
4. Build the message list (system prompt + memories + recent history + new turn).
5. Stream the completion back to the client over SSE.
6. After the turn completes, persist both messages and store a summarized
   long-term memory for next time.

Kept intentionally thin: all real logic (LLM calls, memory) lives in
app/services and app/memory — this file only orchestrates.
"""

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.memory.store import memory_store
from app.models.db import Attachment
from app.models.schemas import ChatMessageIn
from app.services.history import add_message, get_or_create_conversation, get_recent_messages
from app.services.openrouter_client import openrouter_client

router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_PROMPT = (
    "You are Anqa, a helpful, precise AI assistant with long-term memory "
    "of the user. Use the MEMORY block below only if it's relevant to the "
    "current message; otherwise ignore it."
)


async def _resolve_attachments(
    db: AsyncSession, user_id: str, attachment_ids: list[str]
) -> list[str]:
    """attachment_ids (client-supplied) -> image URLs (server-verified).

    Only URLs for image attachments owned by this user are returned —
    never trust the client's own claim about what an attachment_id is.
    """
    if not attachment_ids:
        return []
    result = await db.execute(
        select(Attachment).where(
            Attachment.id.in_(attachment_ids),
            Attachment.user_id == user_id,
            Attachment.type == "image",
        )
    )
    return [row.url for row in result.scalars().all()]


def _build_messages(
    user_text: str, memories: list[dict], recent_history: list, image_urls: list[str]
) -> list[dict]:
    memory_block = "\n".join(f"- {m['text']}" for m in memories) or "(no relevant memories)"
    system = f"{SYSTEM_PROMPT}\n\nMEMORY:\n{memory_block}"
    messages = [{"role": "system", "content": system}]
    for msg in recent_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append(openrouter_client.build_user_message(user_text, image_urls))
    return messages


@router.post("/send")
async def send_message(
    payload: ChatMessageIn,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message and stream the assistant's reply back as
    Server-Sent Events. Each event is a JSON chunk: {"delta": "..."}.
    """
    conversation = await get_or_create_conversation(db, user_id, payload.conversation_id)
    conversation_id = conversation.id

    # Step 1: resolve attachment_ids -> image URLs (server-verified, not client-trusted)
    image_urls = await _resolve_attachments(db, user_id, payload.attachment_ids)

    # Step 2: pull relevant long-term memory for this user
    memories = memory_store.retrieve(user_id=user_id, query=payload.content)

    # Step 3: recent turns in *this* conversation, for short-term continuity
    recent_history = await get_recent_messages(db, conversation_id, limit=20)

    # Step 4: persist the incoming user message now, before streaming starts
    await add_message(db, conversation_id, role="user", content=payload.content)
    await db.commit()

    messages = _build_messages(payload.content, memories, recent_history, image_urls)

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

        # Step 5: persist the assistant reply + store a long-term memory summary
        if full_reply:
            await add_message(db, conversation_id, role="assistant", content=full_reply)
            await db.commit()

        if payload.content and full_reply:
            summary = f"User asked: {payload.content[:200]} | Assistant replied: {full_reply[:200]}"
            memory_store.add_memory(user_id=user_id, text=summary, conversation_id=conversation_id)

        yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
