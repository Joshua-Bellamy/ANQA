"""
app/memory/store.py

Anqa's long-term memory. This is the piece that turns a normal chatbot
into one with "powerful memory": every meaningful exchange gets embedded
and stored, and relevant past memories are retrieved and injected into
future conversations — even in a brand new chat session.

Design:
- chromadb (local, file-based) so the project runs with zero cloud cost.
- Each memory is stored with metadata (user_id, timestamp, conversation_id)
  so retrieval can be scoped per-user.
- Retrieval uses cosine similarity search (chromadb default) over the
  `memory_top_k` most relevant items, configured in core/config.py.

To swap to a hosted vector DB later (Qdrant, Pinecone, pgvector), only
this file changes — routers and services call `memory_store`, never
chromadb directly.
"""

import uuid
from datetime import datetime, timezone

import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings


class MemoryStore:
    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(path=settings.vector_store_path)
        # Sentence-transformers runs locally — no extra API cost/key needed
        # just to embed memories. Swap for an OpenRouter/OpenAI embedding
        # model later if you want higher-quality retrieval.
        self._embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self._collection = self._client.get_or_create_collection(
            name="anqa_memories",
            embedding_function=self._embedder,
        )

    def add_memory(self, user_id: str, text: str, conversation_id: str) -> str:
        """Store one memory item (e.g. a summarized fact from a conversation)."""
        memory_id = str(uuid.uuid4())
        self._collection.add(
            ids=[memory_id],
            documents=[text],
            metadatas=[{
                "user_id": user_id,
                "conversation_id": conversation_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }],
        )
        return memory_id

    def retrieve(self, user_id: str, query: str, top_k: int | None = None) -> list[dict]:
        """
        Retrieve the most relevant past memories for this user given the
        current query text. Called before every LLM request so the model
        gets relevant context even from long-past conversations.
        """
        k = top_k or settings.memory_top_k
        results = self._collection.query(
            query_texts=[query],
            n_results=k,
            where={"user_id": user_id},
        )
        memories = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]
        for doc, meta, dist, _id in zip(docs, metas, dists, ids):
            memories.append({
                "id": _id,
                "text": doc,
                "score": 1 - dist,  # convert distance -> similarity score
                "created_at": meta.get("created_at"),
            })
        return memories


# Singleton — imported wherever memory read/write is needed
memory_store = MemoryStore()
