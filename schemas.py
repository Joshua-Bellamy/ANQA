"""
app/models/schemas.py

All Pydantic request/response models live here. Keeping schemas separate
from routers and services is deliberate: it means the "shape" of the API
can be read and reviewed in one file, independent of business logic.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class AttachmentType(str, Enum):
    image = "image"
    video = "video"
    pdf = "pdf"
    file = "file"
    audio = "audio"


class Attachment(BaseModel):
    """A file that was uploaded and attached to a chat message."""
    id: str
    type: AttachmentType
    filename: str
    url: str  # where the stored file (or its extracted text) can be fetched
    mime_type: str


class ChatMessageIn(BaseModel):
    """What the client sends when the user sends a message."""
    conversation_id: str | None = None
    content: str = Field(default="", description="Text content of the message")
    attachment_ids: list[str] = Field(default_factory=list)
    stream: bool = True


class ChatMessageOut(BaseModel):
    """A single message as stored/returned by the API."""
    id: str
    conversation_id: str
    role: Role
    content: str
    attachments: list[Attachment] = Field(default_factory=list)
    created_at: datetime


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MemoryItem(BaseModel):
    """A single fact/summary retrieved from long-term memory."""
    id: str
    text: str
    score: float
    created_at: datetime


class TranscriptionOut(BaseModel):
    """Result of speech-to-text on an uploaded audio clip."""
    text: str
    language: str | None = None


class TTSRequest(BaseModel):
    text: str
    voice: str = "default"


class UploadOut(BaseModel):
    attachment: Attachment
    extracted_text_preview: str | None = None
