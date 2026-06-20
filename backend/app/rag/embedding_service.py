import logging

from langchain_openai import OpenAIEmbeddings

from app.core.config import settings  # noqa: F401

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSIONS = 1536
EMBEDDING_MODEL = "text-embedding-3-small"


class EmbeddingGenerationError(Exception):
    """Raised when text embedding generation fails."""


class EmbeddingService:
    def __init__(self) -> None:
        self._embeddings: OpenAIEmbeddings | None = None

    @property
    def embeddings(self) -> OpenAIEmbeddings:
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                dimensions=EMBEDDING_DIMENSIONS,
            )
        return self._embeddings

    def create_embedding(self, text: str) -> list[float]:
        try:
            vector = self.embeddings.embed_query(text)
            return list(vector)
        except Exception as exc:
            logger.error(
                "Embedding generation failed: %s",
                exc,
                exc_info=True,
            )
            raise EmbeddingGenerationError(
                "Failed to generate embedding"
            ) from exc
