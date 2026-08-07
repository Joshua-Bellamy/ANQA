from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Conversation, Message


async def get_or_create_conversation(
    db: AsyncSession, user_id: str, conversation_id: str | None
) -> Conversation:
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.user_id == user_id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    await db.flush()
    return conversation


async def add_message(db: AsyncSession, conversation_id: str, role: str, content: str) -> Message:
    message = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    await db.flush()
    return message


async def get_recent_messages(
    db: AsyncSession, conversation_id: str, limit: int = 20
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    messages.reverse()
    return messages


async def list_conversations(db: AsyncSession, user_id: str) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())
